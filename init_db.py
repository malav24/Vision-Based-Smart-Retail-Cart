import sqlite3
import os
from werkzeug.security import generate_password_hash
from config import DATABASE, BASE_DIR

def init_db():
    schema_path = os.path.join(BASE_DIR, 'database', 'schema.sql')
    if not os.path.exists(DATABASE):
        os.makedirs(os.path.dirname(DATABASE), exist_ok=True)
    
    with sqlite3.connect(DATABASE) as conn:
        with open(schema_path, 'r') as f:
            conn.executescript(f.read())
        
        # Insert default admin user if not exists
        cur = conn.execute("SELECT id FROM admins WHERE username = 'admin'")
        if not cur.fetchone():
            hashed_pass = generate_password_hash("admin")
            conn.execute("INSERT INTO admins (username, password_hash) VALUES (?, ?)", ('admin', hashed_pass))
        conn.commit()
        
    print("Database initialized successfully!")

if __name__ == '__main__':
    init_db()
