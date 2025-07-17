import sqlite3
import time
import os
import sys

# اضافه کردن مسیر پروژه
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from utils.ai_helper import get_hafez_interpretation_groq, get_fallback_interpretation

def generate_interpretations():
    conn = sqlite3.connect('database/hafez.db')
    cursor = conn.cursor()
    
    # دریافت 5 غزل اول (برای تست)
    cursor.execute('SELECT id, number, text FROM ghazals ORDER BY number')
    ghazals = cursor.fetchall()
    
    print(f"🔄 شروع پردازش {len(ghazals)} غزل...")
    
    for i, (ghazal_id, number, text) in enumerate(ghazals, 1):
        print(f"🔄 ({i}/{len(ghazals)}) غزل {number}...")
        
        # چک کن قبلاً پردازش شده؟
        cursor.execute('''
            SELECT COUNT(*) FROM interpretations 
            WHERE ghazal_id = ? AND interpretation_type = 'fal'
        ''', (ghazal_id,))
        
        if cursor.fetchone()[0] > 0:
            print(f"⏭️  قبلاً پردازش شده")
            continue
        
        # دریافت تفسیر
        interpretation = get_hafez_interpretation_groq(text, number, 'fal')
        
        if interpretation:
            # ذخیره تفسیر AI
            cursor.execute('''
                INSERT INTO interpretations (ghazal_id, interpretation_type, interpretation, source)
                VALUES (?, ?, ?, ?)
            ''', (ghazal_id, 'fal', interpretation, 'ai'))
            
            print(f"✅ موفق - AI")
        else:
            # تفسیر fallback
            fallback = get_fallback_interpretation(text, number)
            cursor.execute('''
                INSERT INTO interpretations (ghazal_id, interpretation_type, interpretation, source)
                VALUES (?, ?, ?, ?)
            ''', (ghazal_id, 'fal', fallback, 'fallback'))
            
            print(f"🔄 fallback استفاده شد")
        
        conn.commit()
        
        # تاخیر 3 ثانیه
        time.sleep(3)
    
    conn.close()
    print(f"\n✅ تمام شد!")

if __name__ == "__main__":
    generate_interpretations()