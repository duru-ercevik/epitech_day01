from functools import wraps

from flask import Flask, g, jsonify, request, session
from werkzeug.security import generate_password_hash, check_password_hash

from db import get_db, close_db, init_db, database_exists

app = Flask(__name__)
app.config["SECRET_KEY"] = "dev-secret-degistir"
app.json.ensure_ascii = False  # Türkçe karakterler bozulmasın

app.teardown_appcontext(close_db)  # her istek bitince bağlantıyı kapat

# Veritabanı dosyası yoksa tabloları oluştur
if not database_exists():
    init_db()

ROLES = ["user", "recruiter", "admin"]


# --- YARDIMCI FONKSİYONLAR ---

def row_to_dict(row, bool_fields=()):
    """sqlite3 satırını sözlüğe çevirir. SQLite true/false'u 1/0 olarak
    sakladığı için istenen alanları tekrar True/False yapar."""
    if row is None:
        return None
    result = dict(row)
    for field in bool_fields:
        if field in result:
            result[field] = bool(result[field])
    return result


def hash_password(password):
    return generate_password_hash(password, method="pbkdf2:sha256")


def update_fields(table, record_id, data, allowed_fields):
    """data içinde gelen ve izin verilen alanlar için UPDATE sorgusu kurar.
    Sütun adları sadece bizim yazdığımız allowed_fields listesinden geldiği
    için güvenli; kullanıcıdan gelen değerler ise ? ile ayrıca gönderiliyor."""
    fields = [field for field in allowed_fields if field in data]
    if not fields:
        return
    set_clause = ", ".join(f"{field} = ?" for field in fields)
    values = [data[field] for field in fields] + [record_id]
    get_db().execute(f"UPDATE {table} SET {set_clause} WHERE id = ?", values)


# Sık kullanılan SELECT sorguları
AD_SELECT = """
    SELECT a.*, c.name AS company_name
    FROM advertisements a
    LEFT JOIN companies c ON a.company_id = c.id
"""

# password_hash bilerek yok: şifre hiçbir zaman dışarı gönderilmiyor
PERSON_SELECT = """
    SELECT p.id, p.first_name, p.last_name, p.email, p.phone, p.role,
           p.company_id, c.name AS company_name, p.created_at
    FROM people p
    LEFT JOIN companies c ON p.company_id = c.id
"""

APPLICATION_SELECT = """
    SELECT ap.*, a.title AS ad_title, a.company_id AS company_id
    FROM applications ap
    LEFT JOIN advertisements a ON ap.ad_id = a.id
"""


def find_ad(ad_id):
    row = get_db().execute(AD_SELECT + " WHERE a.id = ?", (ad_id,)).fetchone()
    return row_to_dict(row, ["is_active"])


def find_company(company_id):
    row = get_db().execute("SELECT * FROM companies WHERE id = ?", (company_id,)).fetchone()
    return row_to_dict(row)


def find_person(person_id):
    row = get_db().execute(PERSON_SELECT + " WHERE p.id = ?", (person_id,)).fetchone()
    return row_to_dict(row)


def find_application(application_id):
    row = get_db().execute(APPLICATION_SELECT + " WHERE ap.id = ?", (application_id,)).fetchone()
    return row_to_dict(row, ["email_sent"])

def paginate(sql, params=(), bool_fields=()):
    """Bir SELECT sorgusunu sayfalara böler.
    ?page=2&limit=10 gibi query parametrelerini okur, toplam kayıt sayısıyla
    birlikte sadece istenen sayfadaki kayıtları döndürür."""
    page = request.args.get("page", default=1, type=int)
    limit = request.args.get("limit", default=10, type=int)

    # Geçersiz değerlere karşı sınırlar
    page = max(page, 1)
    limit = min(max(limit, 1), 100)

    db = get_db()
    total = db.execute(f"SELECT COUNT(*) FROM ({sql})", params).fetchone()[0]

    offset = (page - 1) * limit
    rows = db.execute(f"{sql} LIMIT ? OFFSET ?", [*params, limit, offset]).fetchall()

    return jsonify({
        "items": [row_to_dict(row, bool_fields) for row in rows],
        "page": page,
        "limit": limit,
        "total": total,
        "pages": (total + limit - 1) // limit,  # yukarı yuvarlanmış sayfa sayısı
    })


def count_admins():
    return get_db().execute("SELECT COUNT(*) FROM people WHERE role = 'admin'").fetchone()[0]


# --- GİRİŞ / YETKİ ---

def get_current_user():
    """Session'daki kullanıcıyı döndürür, giriş yapılmamışsa None."""
    user_id = session.get("user_id")
    if user_id is None:
        return None
    return find_person(user_id)


def login_required(view):
    """Giriş yapılmamışsa 401 döner. Giriş yapan kişi g.user içine konur."""
    @wraps(view)
    def wrapper(*args, **kwargs):
        g.user = get_current_user()
        if g.user is None:
            return jsonify({"error": "Bu işlem için giriş yapmalısınız"}), 401
        return view(*args, **kwargs)
    return wrapper


def roles_required(*allowed_roles):
    """Giriş yoksa 401, rol listede değilse 403 döner.
    Kullanım: @roles_required("admin") veya @roles_required("admin", "recruiter")"""
    def decorator(view):
        @wraps(view)
        def wrapper(*args, **kwargs):
            g.user = get_current_user()
            if g.user is None:
                return jsonify({"error": "Bu işlem için giriş yapmalısınız"}), 401
            if g.user["role"] not in allowed_roles:
                return jsonify({"error": "Bu işlem için yetkiniz yok"}), 403
            return view(*args, **kwargs)
        return wrapper
    return decorator


def is_admin():
    return g.user["role"] == "admin"


def owns_company(company_id):
    """Recruiter bu şirkette mi çalışıyor? Admin için her zaman True."""
    return is_admin() or g.user["company_id"] == company_id


# --- KAYIT / GİRİŞ ROUTE'LARI ---

# Kayıt ol (herkese açık)
@app.route("/api/auth/register", methods=["POST"])
def register():
    data = request.get_json()

    required = ["first_name", "last_name", "email", "password"]
    if not data or any(not data.get(field) for field in required):
        return jsonify({"error": "first_name, last_name, email ve password zorunlu"}), 400

    if len(data["password"]) < 6:
        return jsonify({"error": "Şifre en az 6 karakter olmalı"}), 400

    email = data["email"].strip().lower()
    db = get_db()

    if db.execute("SELECT id FROM people WHERE email = ?", (email,)).fetchone():
        return jsonify({"error": "Bu e-posta zaten kayıtlı"}), 409

    # role sorguya sabit olarak 'user' yazılıyor, istekten hiç okunmuyor.
    # Recruiter ve admin hesaplarını sadece admin açabilir.
    cursor = db.execute(
        """
        INSERT INTO people (first_name, last_name, email, phone, password_hash, role)
        VALUES (?, ?, ?, ?, ?, 'user')
        """,
        (data["first_name"], data["last_name"], email, data.get("phone"),
         hash_password(data["password"])),
    )
    db.commit()

    session.clear()
    session["user_id"] = cursor.lastrowid
    return jsonify(find_person(cursor.lastrowid)), 201


# Giriş yap (herkese açık)
@app.route("/api/auth/login", methods=["POST"])
def login():
    data = request.get_json()

    if not data or not data.get("email") or not data.get("password"):
        return jsonify({"error": "email ve password zorunlu"}), 400

    email = data["email"].strip().lower()
    row = get_db().execute(
        "SELECT id, password_hash FROM people WHERE email = ?", (email,)
    ).fetchone()

    # E-posta yoksa da, şifre yanlışsa da aynı mesaj
    if row is None or row["password_hash"] is None or not check_password_hash(row["password_hash"], data["password"]):
        return jsonify({"error": "E-posta veya şifre hatalı"}), 401

    session.clear()
    session["user_id"] = row["id"]
    return jsonify(find_person(row["id"]))


# Çıkış yap
@app.route("/api/auth/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"message": "Çıkış yapıldı"})


# Şu an kim giriş yapmış?
@app.route("/api/auth/me", methods=["GET"])
@login_required
def me():
    return jsonify(g.user)


# Kullanıcının kendi hesabını düzenlemesi
@app.route("/api/auth/me", methods=["PUT"])
@login_required
def update_me():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Güncellenecek veri gönderilmedi"}), 400

    for field in ["first_name", "last_name", "email"]:
        if field in data and not data[field]:
            return jsonify({"error": f"{field} boş olamaz"}), 400

    db = get_db()
    user_id = g.user["id"]

    if "email" in data:
        data["email"] = data["email"].strip().lower()
        if db.execute("SELECT id FROM people WHERE email = ? AND id != ?",
                      (data["email"], user_id)).fetchone():
            return jsonify({"error": "Bu e-posta başka bir kişiye ait"}), 409

    if data.get("password"):
        if len(data["password"]) < 6:
            return jsonify({"error": "Şifre en az 6 karakter olmalı"}), 400
        db.execute("UPDATE people SET password_hash = ? WHERE id = ?",
                   (hash_password(data["password"]), user_id))

    # role ve company_id bu listede YOK: kullanıcı bunları kendisi değiştiremez
    update_fields("people", user_id, data, ["first_name", "last_name", "email", "phone"])
    db.commit()
    return jsonify(find_person(user_id))


@app.route("/")
def home():
    return "Job Board API çalışıyor"


# --- İLANLAR ---

# READ: tüm ilanlar (herkese açık)
@app.route("/api/ads", methods=["GET"])
def list_ads():
     return paginate(AD_SELECT + " ORDER BY a.id", bool_fields=["is_active"])


# READ: tek ilan (herkese açık)
@app.route("/api/ads/<int:ad_id>", methods=["GET"])
def get_ad(ad_id):
    ad = find_ad(ad_id)
    if ad is None:
        return jsonify({"error": "İlan bulunamadı"}), 404
    return jsonify(ad)


def check_contact_person(contact_person_id, company_id):
    """İlan sorumlusu verildiyse geçerli mi? Hata mesajı ya da None döner."""
    if contact_person_id is None:
        return None
    person = find_person(contact_person_id)
    if person is None:
        return "Sorumlu kişi bulunamadı"
    if person["role"] == "recruiter" and person["company_id"] != company_id:
        return "Sorumlu kişi bu şirkette çalışmıyor"
    return None


# CREATE: yeni ilan (admin her şirkete, recruiter sadece kendi şirketine)
@app.route("/api/ads", methods=["POST"])
@roles_required("admin", "recruiter")
def create_ad():
    data = request.get_json()

    if not data or not data.get("title") or not data.get("short_description"):
        return jsonify({"error": "title ve short_description zorunlu"}), 400

    if is_admin():
        company_id = data.get("company_id")
        if not company_id:
            return jsonify({"error": "company_id zorunlu"}), 400
        contact_person_id = data.get("contact_person_id")
    else:
        # Recruiter'ın ilanı her zaman kendi şirketine ait olur,
        # istekte başka bir company_id gönderse bile dikkate alınmaz
        company_id = g.user["company_id"]
        contact_person_id = data.get("contact_person_id", g.user["id"])

    if find_company(company_id) is None:
        return jsonify({"error": "Şirket bulunamadı"}), 400

    error = check_contact_person(contact_person_id, company_id)
    if error:
        return jsonify({"error": error}), 400

    db = get_db()
    cursor = db.execute(
        """
        INSERT INTO advertisements
            (title, short_description, full_description, salary,
             location, working_time, contract_type, company_id, contact_person_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            data["title"],
            data["short_description"],
            data.get("full_description"),
            data.get("salary"),
            data.get("location"),
            data.get("working_time"),
            data.get("contract_type"),
            company_id,
            contact_person_id,
        ),
    )
    db.commit()
    return jsonify(find_ad(cursor.lastrowid)), 201


# UPDATE: ilanı güncelle (admin hepsini, recruiter sadece kendi şirketininkileri)
@app.route("/api/ads/<int:ad_id>", methods=["PUT"])
@roles_required("admin", "recruiter")
def update_ad(ad_id):
    ad = find_ad(ad_id)
    if ad is None:
        return jsonify({"error": "İlan bulunamadı"}), 404
    if not owns_company(ad["company_id"]):
        return jsonify({"error": "Bu ilan sizin şirketinize ait değil"}), 403

    data = request.get_json()
    if not data:
        return jsonify({"error": "Güncellenecek veri gönderilmedi"}), 400

    allowed_fields = [
        "title", "short_description", "full_description", "salary",
        "location", "working_time", "contract_type", "is_active",
        "contact_person_id",
    ]

    # İlanı başka şirkete sadece admin taşıyabilir
    if is_admin():
        allowed_fields.append("company_id")
        if "company_id" in data and find_company(data["company_id"]) is None:
            return jsonify({"error": "Şirket bulunamadı"}), 400

    final_company_id = data["company_id"] if "company_id" in allowed_fields and "company_id" in data else ad["company_id"]
    if "contact_person_id" in data:
        error = check_contact_person(data["contact_person_id"], final_company_id)
        if error:
            return jsonify({"error": error}), 400

    update_fields("advertisements", ad_id, data, allowed_fields)
    get_db().commit()
    return jsonify(find_ad(ad_id))


# DELETE: ilanı sil (admin hepsini, recruiter sadece kendi şirketininkileri)
@app.route("/api/ads/<int:ad_id>", methods=["DELETE"])
@roles_required("admin", "recruiter")
def delete_ad(ad_id):
    ad = find_ad(ad_id)
    if ad is None:
        return jsonify({"error": "İlan bulunamadı"}), 404
    if not owns_company(ad["company_id"]):
        return jsonify({"error": "Bu ilan sizin şirketinize ait değil"}), 403

    db = get_db()
    # Başvurular ON DELETE CASCADE sayesinde otomatik silinir
    db.execute("DELETE FROM advertisements WHERE id = ?", (ad_id,))
    db.commit()
    return jsonify({"message": f"{ad_id} numaralı ilan silindi"})


# --- ŞİRKETLER ---

# READ: tüm şirketler (herkese açık, ilan sayfasında şirket bilgisi gösteriliyor)
@app.route("/api/companies", methods=["GET"])
def list_companies():
    return paginate("SELECT * FROM companies ORDER BY id")


# READ: tek şirket (herkese açık)
@app.route("/api/companies/<int:company_id>", methods=["GET"])
def get_company(company_id):
    company = find_company(company_id)
    if company is None:
        return jsonify({"error": "Şirket bulunamadı"}), 404
    return jsonify(company)


# CREATE: yeni şirket (sadece admin)
@app.route("/api/companies", methods=["POST"])
@roles_required("admin")
def create_company():
    data = request.get_json()

    if not data or not data.get("name"):
        return jsonify({"error": "name zorunlu"}), 400

    db = get_db()
    cursor = db.execute(
        "INSERT INTO companies (name, description, website, city) VALUES (?, ?, ?, ?)",
        (data["name"], data.get("description"), data.get("website"), data.get("city")),
    )
    db.commit()
    return jsonify(find_company(cursor.lastrowid)), 201


# UPDATE: şirketi güncelle (admin her şirketi, recruiter kendi şirketini)
@app.route("/api/companies/<int:company_id>", methods=["PUT"])
@roles_required("admin", "recruiter")
def update_company(company_id):
    if find_company(company_id) is None:
        return jsonify({"error": "Şirket bulunamadı"}), 404
    if not owns_company(company_id):
        return jsonify({"error": "Bu şirkette çalışmıyorsunuz"}), 403

    data = request.get_json()
    if not data:
        return jsonify({"error": "Güncellenecek veri gönderilmedi"}), 400

    if "name" in data and not data["name"]:
        return jsonify({"error": "name boş olamaz"}), 400

    update_fields("companies", company_id, data, ["name", "description", "website", "city"])
    get_db().commit()
    return jsonify(find_company(company_id))


# DELETE: şirketi sil (sadece admin)
@app.route("/api/companies/<int:company_id>", methods=["DELETE"])
@roles_required("admin")
def delete_company(company_id):
    if find_company(company_id) is None:
        return jsonify({"error": "Şirket bulunamadı"}), 404

    db = get_db()
    # Şirketsiz kalan recruiter'lar normal kullanıcıya döner
    db.execute(
        "UPDATE people SET role = 'user', company_id = NULL WHERE company_id = ?",
        (company_id,),
    )
    # İlanlar ve onların başvuruları ON DELETE CASCADE ile otomatik silinir
    db.execute("DELETE FROM companies WHERE id = ?", (company_id,))
    db.commit()
    return jsonify({"message": f"{company_id} numaralı şirket silindi"})


# --- KİŞİLER (sadece admin) ---

def validate_role_and_company(role, company_id):
    """Rol ve şirket birlikte tutarlı mı? Hata mesajı ya da None döner."""
    if role not in ROLES:
        return "role sadece 'user', 'recruiter' veya 'admin' olabilir"
    if role == "recruiter":
        if not company_id:
            return "recruiter için company_id zorunlu"
        if find_company(company_id) is None:
            return "Şirket bulunamadı"
    return None


# READ: tüm kişiler
@app.route("/api/people", methods=["GET"])
@roles_required("admin")
def list_people():
    return paginate(PERSON_SELECT + " ORDER BY p.id")


# READ: tek kişi
@app.route("/api/people/<int:person_id>", methods=["GET"])
@roles_required("admin")
def get_person(person_id):
    person = find_person(person_id)
    if person is None:
        return jsonify({"error": "Kişi bulunamadı"}), 404
    return jsonify(person)


# CREATE: yeni kişi (recruiter ve admin hesapları buradan açılır)
@app.route("/api/people", methods=["POST"])
@roles_required("admin")
def create_person():
    data = request.get_json()

    if not data or not data.get("first_name") or not data.get("last_name") or not data.get("email"):
        return jsonify({"error": "first_name, last_name ve email zorunlu"}), 400

    email = data["email"].strip().lower()
    db = get_db()

    if db.execute("SELECT id FROM people WHERE email = ?", (email,)).fetchone():
        return jsonify({"error": "Bu e-posta zaten kayıtlı"}), 409

    role = data.get("role", "user")
    company_id = data.get("company_id") if role == "recruiter" else None

    error = validate_role_and_company(role, company_id)
    if error:
        return jsonify({"error": error}), 400

    password_hash = hash_password(data["password"]) if data.get("password") else None

    cursor = db.execute(
        """
        INSERT INTO people (first_name, last_name, email, phone, password_hash, role, company_id)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (data["first_name"], data["last_name"], email, data.get("phone"),
         password_hash, role, company_id),
    )
    db.commit()
    return jsonify(find_person(cursor.lastrowid)), 201


# UPDATE: kişiyi güncelle
@app.route("/api/people/<int:person_id>", methods=["PUT"])
@roles_required("admin")
def update_person(person_id):
    person = find_person(person_id)
    if person is None:
        return jsonify({"error": "Kişi bulunamadı"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "Güncellenecek veri gönderilmedi"}), 400

    for field in ["first_name", "last_name", "email"]:
        if field in data and not data[field]:
            return jsonify({"error": f"{field} boş olamaz"}), 400

    db = get_db()

    if "email" in data:
        data["email"] = data["email"].strip().lower()
        if db.execute("SELECT id FROM people WHERE email = ? AND id != ?",
                      (data["email"], person_id)).fetchone():
            return jsonify({"error": "Bu e-posta başka bir kişiye ait"}), 409

    # Güncellemeden sonraki rol ve şirketi hesapla, birlikte kontrol et
    if "role" in data or "company_id" in data:
        new_role = data.get("role", person["role"])
        new_company_id = data.get("company_id", person["company_id"]) if new_role == "recruiter" else None

        error = validate_role_and_company(new_role, new_company_id)
        if error:
            return jsonify({"error": error}), 400

        # Son admin, yetkisi alınarak da kaybolmasın
        if person["role"] == "admin" and new_role != "admin" and count_admins() <= 1:
            return jsonify({"error": "Son admin'in yetkisi alınamaz"}), 400

        db.execute("UPDATE people SET role = ?, company_id = ? WHERE id = ?",
                   (new_role, new_company_id, person_id))

    if data.get("password"):
        db.execute("UPDATE people SET password_hash = ? WHERE id = ?",
                   (hash_password(data["password"]), person_id))

    update_fields("people", person_id, data, ["first_name", "last_name", "email", "phone"])
    db.commit()
    return jsonify(find_person(person_id))


# DELETE: kişiyi sil
@app.route("/api/people/<int:person_id>", methods=["DELETE"])
@roles_required("admin")
def delete_person(person_id):
    person = find_person(person_id)
    if person is None:
        return jsonify({"error": "Kişi bulunamadı"}), 404

    if person["role"] == "admin" and count_admins() <= 1:
        return jsonify({"error": "Son admin silinemez"}), 400

    db = get_db()
    # İlanları ve başvuruları silinmez: ON DELETE SET NULL ile bağlantı boşalır
    db.execute("DELETE FROM people WHERE id = ?", (person_id,))
    db.commit()
    return jsonify({"message": f"{person_id} numaralı kişi silindi"})


# --- BAŞVURULAR ---

# READ: başvurular (admin hepsini, recruiter sadece kendi şirketinin ilanlarına gelenleri)
@app.route("/api/applications", methods=["GET"])
@roles_required("admin", "recruiter")
def list_applications():
    sql = APPLICATION_SELECT
    conditions = []
    params = []

    if not is_admin():
        conditions.append("a.company_id = ?")
        params.append(g.user["company_id"])

    ad_id = request.args.get("ad_id", type=int)
    if ad_id is not None:
        conditions.append("ap.ad_id = ?")
        params.append(ad_id)

    if conditions:
        sql += " WHERE " + " AND ".join(conditions)

    sql += " ORDER BY ap.created_at DESC, ap.id DESC"
    return paginate(sql, params, bool_fields=["email_sent"])


# READ: tek başvuru
@app.route("/api/applications/<int:application_id>", methods=["GET"])
@roles_required("admin", "recruiter")
def get_application(application_id):
    application = find_application(application_id)
    if application is None:
        return jsonify({"error": "Başvuru bulunamadı"}), 404
    if not owns_company(application["company_id"]):
        return jsonify({"error": "Bu başvuru sizin şirketinizin ilanına ait değil"}), 403
    return jsonify(application)


# CREATE: yeni başvuru (herkese açık, "Apply" butonu bunu kullanacak)
@app.route("/api/applications", methods=["POST"])
def create_application():
    data = request.get_json() or {}

    if not data.get("ad_id"):
        return jsonify({"error": "ad_id zorunlu"}), 400

    ad = find_ad(data["ad_id"])
    if ad is None:
        return jsonify({"error": "İlan bulunamadı"}), 404
    if not ad["is_active"]:
        return jsonify({"error": "Bu ilan artık başvuru kabul etmiyor"}), 400

    user = get_current_user()
    if user:
        # Giriş yapmış kullanıcı bilgilerini tekrar yazmak zorunda değil:
        # ad, e-posta ve telefon hesabından alınır
        person_id = user["id"]
        name = f"{user['first_name']} {user['last_name']}"
        email = user["email"]
        phone = user["phone"]
    else:
        if not data.get("name") or not data.get("email"):
            return jsonify({"error": "name ve email zorunlu"}), 400
        person_id = None
        name = data["name"]
        email = data["email"].strip().lower()
        phone = data.get("phone")

    db = get_db()

    # Aynı kişi aynı ilana iki kez başvurmasın
    if db.execute("SELECT id FROM applications WHERE ad_id = ? AND email = ?",
                  (ad["id"], email)).fetchone():
        return jsonify({"error": "Bu ilana zaten başvurdunuz"}), 409

    cursor = db.execute(
        """
        INSERT INTO applications (ad_id, person_id, name, email, phone, message)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (ad["id"], person_id, name, email, phone, data.get("message")),
    )
    db.commit()
    return jsonify(find_application(cursor.lastrowid)), 201


# UPDATE: başvuruyu güncelle
@app.route("/api/applications/<int:application_id>", methods=["PUT"])
@roles_required("admin", "recruiter")
def update_application(application_id):
    application = find_application(application_id)
    if application is None:
        return jsonify({"error": "Başvuru bulunamadı"}), 404
    if not owns_company(application["company_id"]):
        return jsonify({"error": "Bu başvuru sizin şirketinizin ilanına ait değil"}), 403

    data = request.get_json()
    if not data:
        return jsonify({"error": "Güncellenecek veri gönderilmedi"}), 400

    if is_admin():
        allowed_fields = ["name", "email", "phone", "message", "email_sent"]
    else:
        # Recruiter adayın bilgilerini değiştiremez, sadece "e-posta gönderildi" işaretler
        allowed_fields = ["email_sent"]

    for field in ["name", "email"]:
        if field in allowed_fields and field in data and not data[field]:
            return jsonify({"error": f"{field} boş olamaz"}), 400

    if "email" in data and "email" in allowed_fields:
        data["email"] = data["email"].strip().lower()

    update_fields("applications", application_id, data, allowed_fields)
    get_db().commit()
    return jsonify(find_application(application_id))


# DELETE: başvuruyu sil (sadece admin)
@app.route("/api/applications/<int:application_id>", methods=["DELETE"])
@roles_required("admin")
def delete_application(application_id):
    if find_application(application_id) is None:
        return jsonify({"error": "Başvuru bulunamadı"}), 404

    db = get_db()
    db.execute("DELETE FROM applications WHERE id = ?", (application_id,))
    db.commit()
    return jsonify({"message": f"{application_id} numaralı başvuru silindi"})


if __name__ == "__main__":
    app.run(debug=True)