import sqlite3

def update_logs_table():
    conn = sqlite3.connect('hafez.db')
    cursor = conn.cursor()
    
    columns = [
        'ALTER TABLE user_logs ADD COLUMN device_type TEXT',
        'ALTER TABLE user_logs ADD COLUMN browser TEXT', 
        'ALTER TABLE user_logs ADD COLUMN os TEXT',
        'ALTER TABLE user_logs ADD COLUMN country TEXT',
        'ALTER TABLE user_logs ADD COLUMN city TEXT',
        'ALTER TABLE user_logs ADD COLUMN region TEXT',
        'ALTER TABLE user_logs ADD COLUMN session_id TEXT'
    ]
    
    for col in columns:
        try:
            cursor.execute(col)
            print(f"✅ Added: {col.split()[-2]}")
        except:
            print(f"⚠️ Exists: {col.split()[-2]}")
    
    conn.commit()
    conn.close()
    print("🎉 Database updated!")

if __name__ == "__main__":
    update_logs_table()