import random
from werkzeug.security import generate_password_hash

from db import connect, init_db

random.seed(42)  # her çalıştırmada aynı veriler oluşsun


def hash_password(password):
    return generate_password_hash(password, method="pbkdf2:sha256")


# Temiz başlangıç: schema.sql tabloları silip yeniden oluşturur
init_db()
conn = connect()


def insert(sql, params):
    """INSERT çalıştırır ve yeni kaydın id'sini döndürür."""
    return conn.execute(sql, params).lastrowid


# ---------- Kişiler ----------
PERSON_SQL = """
    INSERT INTO people (first_name, last_name, email, phone, password_hash, role, company_id)
    VALUES (?, ?, ?, ?, ?, ?, ?)
"""

insert(PERSON_SQL, ("Admin", "User", "admin@jobboard.com", "05550000000",
                    hash_password("admin123"), "admin", None))
user_id = insert(PERSON_SQL, ("Ayşe", "Yılmaz", "ayse@example.com", "05551112233",
                              hash_password("user123"), "user", None))

# ---------- Şirketler ----------
companies = [
    ("TechCorp", "Kurumsal yazılım çözümleri geliştiren teknoloji şirketi.",
     "https://techcorp.example.com", "İstanbul"),
    ("DataFlow", "Veri analitiği ve makine öğrenmesi alanında uzman girişim.",
     "https://dataflow.example.com", "Ankara"),
    ("WebStudio", "Web ve mobil uygulama ajansı.",
     "https://webstudio.example.com", "İzmir"),
    ("CloudNine", "Bulut altyapısı ve DevOps hizmetleri.",
     "https://cloudnine.example.com", "İstanbul"),
]

company_rows = []  # (id, name, city)
for name, description, website, city in companies:
    company_id = insert(
        "INSERT INTO companies (name, description, website, city) VALUES (?, ?, ?, ?)",
        (name, description, website, city),
    )
    company_rows.append((company_id, name, city))

# ---------- Recruiter'lar (her şirkette bir tane) ----------
recruiters = [
    ("Mehmet", "Kaya", "mehmet@techcorp.com", "05552223344"),
    ("Zeynep", "Demir", "zeynep@dataflow.com", "05553334455"),
    ("Can", "Öztürk", "can@webstudio.com", "05554445566"),
    ("Burak", "Şen", "burak@cloudnine.com", "05556667788"),
]
recruiter_by_company = {}  # şirket id -> recruiter id
for (first, last, email, phone), (company_id, _, _) in zip(recruiters, company_rows):
    recruiter_by_company[company_id] = insert(
        PERSON_SQL,
        (first, last, email, phone, hash_password("recruiter123"), "recruiter", company_id),
    )

# ---------- İlanlar ----------
positions = [
    ("Junior Backend Developer", "Python ve Flask ile API geliştirecek ekip arkadaşı arıyoruz."),
    ("Frontend Developer", "Modern JavaScript ile kullanıcı arayüzleri geliştirme."),
    ("Data Analyst Stajyeri", "SQL ve Python ile veri analizi yapacak stajyer."),
    ("DevOps Engineer", "CI/CD süreçlerini ve bulut altyapısını yönetme."),
    ("Mobile Developer", "iOS ve Android uygulamaları geliştirme."),
    ("QA Test Engineer", "Manuel ve otomasyon testleri yazma."),
    ("UI/UX Designer", "Kullanıcı deneyimi odaklı arayüz tasarımı."),
    ("Machine Learning Engineer", "ML modellerini eğitip canlıya alma."),
    ("Full Stack Developer", "Hem backend hem frontend tarafında çalışma."),
    ("IT Support Stajyeri", "Kullanıcı destek ve sistem bakım süreçlerinde görev alma."),
    ("Product Manager", "Ürün yol haritasını belirleme ve ekipleri koordine etme."),
    ("Database Administrator", "Veritabanı performansı ve yedekleme yönetimi."),
    ("Cyber Security Analyst", "Güvenlik açıklarını tespit etme ve raporlama."),
    ("Business Analyst", "İş gereksinimlerini analiz edip dokümante etme."),
    ("Software Engineer Intern", "Yaz dönemi yazılım mühendisliği stajı."),
    ("Cloud Architect", "Ölçeklenebilir bulut mimarileri tasarlama."),
    ("Technical Writer", "Teknik dokümantasyon hazırlama."),
    ("Scrum Master", "Agile süreçlerini yönetme ve ekibe rehberlik etme."),
    ("Game Developer", "Unity ile oyun geliştirme."),
    ("Data Engineer", "Veri boru hatları (pipeline) kurma ve yönetme."),
]
working_times = ["Tam zamanlı", "Yarı zamanlı", "Hibrit", "Uzaktan"]
contract_types = ["Kalıcı", "Staj", "Sözleşmeli"]
salaries = ["25.000 - 35.000 TL", "35.000 - 50.000 TL", "50.000 - 70.000 TL", "Görüşmede belirlenecek"]

ad_ids = []
for title, short in positions:
    company_id, company_name, city = random.choice(company_rows)
    full = (
        f"{company_name} olarak {title} pozisyonu için ekibimize katılacak "
        f"yeni bir arkadaş arıyoruz. {short} "
        "Takım çalışmasına yatkın, öğrenmeye açık ve sorumluluk sahibi adaylar tercih sebebidir."
    )
    ad_id = insert(
        """
        INSERT INTO advertisements
            (title, short_description, full_description, salary, location,
             working_time, contract_type, company_id, contact_person_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (title, short, full, random.choice(salaries), city,
         random.choice(working_times), random.choice(contract_types),
         company_id, recruiter_by_company[company_id]),
    )
    ad_ids.append(ad_id)

# ---------- Örnek başvurular ----------
APPLICATION_SQL = """
    INSERT INTO applications (ad_id, person_id, name, email, phone, message)
    VALUES (?, ?, ?, ?, ?, ?)
"""
# Giriş yapmış kullanıcının başvurusu
insert(APPLICATION_SQL, (ad_ids[0], user_id, "Ayşe Yılmaz", "ayse@example.com",
                         "05551112233", "Merhaba, bu pozisyonla çok ilgileniyorum."))
# Giriş yapmadan yapılmış başvuru
insert(APPLICATION_SQL, (ad_ids[2], None, "Ali Vural", "ali.vural@example.com",
                         "05559998877", "Staj için başvurmak istiyorum, CV'mi iletebilirim."))

conn.commit()


def count(table):
    return conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]


print("Veritabanı dolduruldu!")
print(f"  {count('people')} kişi, {count('companies')} şirket, "
      f"{count('advertisements')} ilan, {count('applications')} başvuru")
print("  Admin girişi: admin@jobboard.com / admin123")
print("  Recruiter girişi: mehmet@techcorp.com / recruiter123 (TechCorp)")
print("  Kullanıcı girişi: ayse@example.com / user123")

conn.close()