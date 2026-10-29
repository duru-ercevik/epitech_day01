-- Job Board veritabanı şeması
-- Bu dosya tabloları oluşturur. Önce eski tablolar silinir, sonra baştan kurulur.

DROP TABLE IF EXISTS applications;
DROP TABLE IF EXISTS advertisements;
DROP TABLE IF EXISTS people;
DROP TABLE IF EXISTS companies;

CREATE TABLE companies (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        VARCHAR(120) NOT NULL,
    description TEXT,
    website     VARCHAR(200),
    city        VARCHAR(100),
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE people (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name    VARCHAR(80)  NOT NULL,
    last_name     VARCHAR(80)  NOT NULL,
    email         VARCHAR(120) NOT NULL UNIQUE,
    phone         VARCHAR(30),
    password_hash VARCHAR(255),                       -- giriş yapmayacak kişilerde boş
    role          VARCHAR(20)  NOT NULL DEFAULT 'user'
                  CHECK (role IN ('user', 'recruiter', 'admin')),
    company_id    INTEGER,                            -- sadece recruiter'larda dolu
    created_at    DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE SET NULL
);

CREATE TABLE advertisements (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    title             VARCHAR(150) NOT NULL,
    short_description VARCHAR(300) NOT NULL,
    full_description  TEXT,
    salary            VARCHAR(50),
    location          VARCHAR(100),
    working_time      VARCHAR(50),
    contract_type     VARCHAR(50),
    is_active         BOOLEAN NOT NULL DEFAULT 1,
    created_at        DATETIME DEFAULT CURRENT_TIMESTAMP,

    company_id        INTEGER NOT NULL,
    contact_person_id INTEGER,

    -- Şirket silinirse ilanları da silinir
    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE,
    -- Sorumlu kişi silinirse ilan kalır, sadece bu alan boşalır
    FOREIGN KEY (contact_person_id) REFERENCES people(id) ON DELETE SET NULL
);

CREATE TABLE applications (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    ad_id      INTEGER NOT NULL,
    person_id  INTEGER,                               -- giriş yapmadan başvurulduysa boş

    -- Giriş yapmadan başvuranlar için bilgiler burada da tutuluyor
    name       VARCHAR(160) NOT NULL,
    email      VARCHAR(120) NOT NULL,
    phone      VARCHAR(30),
    message    TEXT,
    email_sent BOOLEAN NOT NULL DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    -- İlan silinirse başvuruları da silinir
    FOREIGN KEY (ad_id) REFERENCES advertisements(id) ON DELETE CASCADE,
    -- Kişi silinirse başvuru kalır, sadece bağlantı boşalır
    FOREIGN KEY (person_id) REFERENCES people(id) ON DELETE SET NULL
);