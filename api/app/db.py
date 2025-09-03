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
                                    modified TIMESTAMP,
                                    summary TEXT DEFAULT NULL);
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
                    text("INSERT INTO tags (name) VALUES (:tag) ON CONFLICT (name) DO NOTHING"),
                    {"tag": tag}
                )
            print("Database initialized successfully.")
    except Exception as e:
        print(f"Error initializing database: {e}")
        raise
# -- jobs --
def create_job(status="PENDING", result=None):
    with engine.begin() as connection:
        result = connection.execute(
            text("INSERT INTO jobs (status, result) VALUES (:status, :result) RETURNING id"),
            {"status": status, "result": result}
        )
        job_id = result.scalar()
        return job_id

def update_job(job_id, status, result=None):
    with engine.begin() as connection:
        connection.execute(
            text("UPDATE jobs SET status = :status, result = :result WHERE id = :job_id"),
            {"status": status, "result": result, "job_id": job_id}
        )

def get_job(job_id):
    with engine.begin() as connection:
        result = connection.execute(
            text("SELECT * FROM jobs WHERE id = :job_id"),
            {"job_id": job_id}
        )
        return result.fetchone()

def get_job_status(job_id):
    job = get_job(job_id)
    if job:
        return job['status']
    return None

# -- folders --

def upsert_folder_count(path, doc_count, last_job_id):
    with engine.begin() as connection:
        connection.execute(
            text("""INSERT INTO folders (path, doc_count, last_scanned, last_job_id)
                    VALUES (:path, :doc_count, NOW(), :last_job_id)
                    ON CONFLICT (path) DO UPDATE 
                    SET doc_count = EXCLUDED.doc_count,
                        last_scanned = NOW(),
                        last_job_id = EXCLUDED.last_job_id;"""),
            {"path": path, "doc_count": doc_count, "last_job_id": last_job_id}
        )

def get_folder_count(path):
    with engine.begin() as connection:
        result = connection.execute(
            text("SELECT doc_count FROM folders WHERE path = :path"),
            {"path": path}
        )
        row = result.mappings().fetchone()
        return row["doc_count"] if row else None
    
# -- documents --

def insert_document(job_id, path, filename, size_kb, modified):
    with engine.begin() as connection:
        connection.execute(
            text("""INSERT INTO documents (job_id, path, filename, size_kb, modified)
                    VALUES (:job_id, :path, :filename, :size_kb, :modified)
                    ON CONFLICT (path) DO UPDATE 
                    SET job_id = EXCLUDED.job_id,
                        filename = EXCLUDED.filename,
                        size_kb = EXCLUDED.size_kb,
                        modified = EXCLUDED.modified;"""),
            {"job_id": job_id, "path": path, "filename": filename, "size_kb": size_kb, "modified": modified}
        )

def get_documents_in_folder(path, limit=10):
    with engine.begin() as connection:
        result = connection.execute(
            text("""
                SELECT d.filename, d.size_kb, d.modified, d.summary,
                       ARRAY_AGG(t.name) AS tags
                FROM documents d
                LEFT JOIN document_tags dt ON d.id = dt.document_id
                LEFT JOIN tags t ON dt.tag_id = t.id
                WHERE d.path LIKE :path_pattern
                GROUP BY d.id
                ORDER BY d.modified DESC
                LIMIT :limit
            """),
            {"path_pattern": f"{path}%", "limit": limit}
        )
        return result.mappings().all()
    
# -- tags --

def tag_document(document_id, tag_name):
    with engine.begin() as connection:
        tag_result = connection.execute(
            text("SELECT id FROM tags WHERE name = :name"),
            {"name": tag_name}
        )
        tag_row = tag_result.fetchone()
        tag_id = tag_row['id']
        
        connection.execute(
            text("""INSERT INTO document_tags (document_id, tag_id)
                    VALUES (:document_id, :tag_id)
                    ON CONFLICT (document_id, tag_id) DO NOTHING;"""),
            {"document_id": document_id, "tag_id": tag_id}
        )

def get_tags_for_document(document_id):
    with engine.begin() as connection:
        result = connection.execute(
            text("""
                SELECT t.name
                FROM tags t
                JOIN document_tags dt ON t.id = dt.tag_id
                WHERE dt.document_id = :document_id
            """),
            {"document_id": document_id}
        )
        return [row['name'] for row in result.fetchall()]