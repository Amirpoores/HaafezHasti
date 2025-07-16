import requests
import sqlite3
import time
import json
from tqdm import tqdm  # برای progress bar

def create_database():
    """ساخت دیتابیس و جداول"""
    conn = sqlite3.connect('database/hafez.db')
    cursor = conn.cursor()
    
    # جدول غزل‌ها
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ghazals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            number INTEGER UNIQUE,
            title TEXT,
            text TEXT,
            topic TEXT,
            audio_file TEXT,
            ganjoor_url TEXT,
            verse_count INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # جدول فال‌ها
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ghazal_id INTEGER,
            user_ip TEXT,
            interpretation TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (ghazal_id) REFERENCES ghazals (id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ دیتابیس آماده شد!")

def fetch_ghazal_from_ganjoor(ghazal_number):
    """دریافت غزل از API گنجور"""
    try:
        url = f"https://api.ganjoor.net/api/ganjoor/page?url=/hafez/ghazal/sh{ghazal_number}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if 'poem' in data:
                poem = data['poem']
                title = poem.get('title', f'غزل {ghazal_number}')
                verses = poem.get('verses', [])
                
                if not verses:
                    return None
                
                # ساخت متن کامل غزل
                full_text = ""
                for verse in verses:
                    if verse.get('text'):
                        full_text += f"{verse['text']}\n"
                
                return {
                    'number': ghazal_number,
                    'title': title,
                    'text': full_text.strip(),
                    'ganjoor_url': url,
                    'verse_count': len(verses)
                }
        
        return None
        
    except Exception as e:
        print(f"❌ خطا در دریافت غزل {ghazal_number}: {e}")
        return None

def save_ghazal_to_db(ghazal_data):
    """ذخیره غزل در دیتابیس"""
    try:
        conn = sqlite3.connect('database/hafez.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO ghazals 
            (number, title, text, topic, audio_file, ganjoor_url, verse_count)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            ghazal_data['number'],
            ghazal_data['title'],
            ghazal_data['text'],
            None,  # topic فعلاً خالی
            f"ghazal_{ghazal_data['number']}.mp3",  # audio_file
            ghazal_data['ganjoor_url'],
            ghazal_data['verse_count']
        ))
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ خطا در ذخیره غزل {ghazal_data['number']}: {e}")
        return False

def fetch_all_ghazals():
    """دریافت تمام غزل‌های حافظ"""
    print("🌹 شروع دریافت غزل‌های حافظ از گنجور...")
    
    # ایجاد دیتابیس
    create_database()
    
    # آمار
    total_ghazals = 495
    success_count = 0
    error_count = 0
    
    # استفاده از tqdm برای progress bar
    for ghazal_number in tqdm(range(1, total_ghazals + 1), desc="دریافت غزل‌ها"):
        # دریافت غزل
        ghazal_data = fetch_ghazal_from_ganjoor(ghazal_number)
        
        if ghazal_data:
            # ذخیره در دیتابیس
            if save_ghazal_to_db(ghazal_data):
                success_count += 1
            else:
                error_count += 1
        else:
            error_count += 1
        
        # تاخیر کوتاه برای محترم بودن به سرور
        time.sleep(0.5)
    
    print(f"\n📊 آمار نهایی:")
    print(f"✅ موفق: {success_count}")
    print(f"❌ ناموفق: {error_count}")
    print(f"📖 کل: {total_ghazals}")

def check_database():
    """بررسی دیتابیس"""
    conn = sqlite3.connect('database/hafez.db')
    cursor = conn.cursor()
    
    # تعداد غزل‌ها
    cursor.execute('SELECT COUNT(*) FROM ghazals')
    total = cursor.fetchone()[0]
    
    # نمونه غزل‌ها
    cursor.execute('SELECT number, title FROM ghazals ORDER BY number LIMIT 5')
    samples = cursor.fetchall()
    
    conn.close()
    
    print(f"\n📚 وضعیت دیتابیس:")
    print(f"📖 تعداد غزل‌ها: {total}")
    print(f"🔍 نمونه‌ها:")
    for number, title in samples:
        print(f"  • {number}: {title}")

if __name__ == '__main__':
    print("🚀 اسکریپت جمع‌آوری غزل‌های حافظ")
    print("1. دریافت تمام غزل‌ها")
    print("2. بررسی دیتابیس")
    
    choice = input("\nانتخاب کنید (1 یا 2): ").strip()
    
    if choice == '1':
        fetch_all_ghazals()
        check_database()
    elif choice == '2':
        check_database()
    else:
        print("❌ انتخاب نامعتبر!")
