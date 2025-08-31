from sqlalchemy import create_engine, text
import os

DB_URL = os.getenv("DB_URL", "postgresql://user:password@postgres:5432/documents")
engine = create_engine(DB_URL)

def init_db():
    try:
        with engine.begin() as connection:
            connection.execute(text("""CREATE TABLE IF NOT EXISTS jobs (
                                    id SERIAL PRIMARY KEY,
                                    status VARCHAR(20),
                                    result TEXT);"""))
            
            connection.execute(text("""CREATE TABLE IF NOT EXISTS folders (
                                    id SERIAL PRIMARY KEY,
                                    path TEXT UNIQUE,
                                    doc_count INT DEFAULT 0,
                                    last_scanned TIMESTAMP,
                                    last_job_id INT,
                                    CONSTRAINT fk_jobs FOREIGN KEY(last_job_id) REFERENCES jobs(id) ON DELETE SET NULL);
                                    """))
            
            connection.execute(text("""CREATE TABLE IF NOT EXISTS documents (
                                    id SERIAL PRIMARY KEY,
                                    job_id INT REFERENCES jobs(id) ON DELETE CASCADE,
                                    path TEXT UNIQUE,
                                    filename VARCHAR(255),
                                    size_kb INT,
                                    created_at TIMESTAMP,
                                    modified_at TIMESTAMP);
                                    """))
            
            connection.execute(text("""CREATE TABLE IF NOT EXISTS tags (
                                    id SERIAL PRIMARY KEY,
                                    name VARCHAR(50) UNIQUE);
                                    """))
            
            connection.execute(text("""CREATE TABLE IF NOT EXISTS document_tags (
                                    document_id INT REFERENCES documents(id) ON DELETE CASCADE,
                                    tag_id INT REFERENCES tags(id) ON DELETE CASCADE,
                                    PRIMARY KEY (document_id, tag_id));
                                    """))
            
            connection.execute(text("""CREATE INDEX IF NOT EXISTS idx_folders_path ON folders(path);"""))
            connection.execute(text("""CREATE INDEX IF NOT EXISTS idx_documents_path ON documents(path);"""))

            internal_document_tags = [
                "Internal Policy",
                "Meeting Notes",
                "Project Documentation",
                "Training Materials",
                "Performance Reviews",
                "Financial Reports",
                "HR Documents",
                "Technical Documentation",
                "Research & Development",
                "Compliance",
                "Internal Communications",
                "Feedback & Surveys",
                "Strategic Planning",
                "Risk Management",
                "Miscellaneous"
            ]
            for tag in internal_document_tags:
                connection.execute(
                    text("INSERT INTO tags (name) VALUES (:t) ON CONFLICT (name) DO NOTHING"),
                    {"t": tag}
                )
            print("Database initialized successfully.")
    except Exception as e:
        print(f"Error initializing database: {e}")
        raise