import sqlite3

def create_logs_table():
    conn = sqlite3.connect('database/hafez.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ip_address TEXT,
            user_agent TEXT,
            action_type TEXT,
            ghazal_number INTEGER,
            search_query TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            referer TEXT,
            page_url TEXT
        )
    ''')

    conn.commit()
    conn.close()
    print("✅ User logs table created successfully!")

if __name__ == "__main__":
    create_logs_table()