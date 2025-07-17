import sqlite3

def create_interpretations_table():
    conn = sqlite3.connect('database/hafez.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS interpretations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ghazal_id INTEGER,
            interpretation_type TEXT DEFAULT 'fal',
            interpretation TEXT,
            source TEXT DEFAULT 'ai',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (ghazal_id) REFERENCES ghazals (id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ جدول interpretations ساخته شد!")

if __name__ == "__main__":
    create_interpretations_table()