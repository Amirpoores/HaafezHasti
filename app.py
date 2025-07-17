from flask import Flask, render_template, jsonify, request
import sqlite3
import random
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

def get_db_connection():
    """اتصال به دیتابیس"""
    conn = sqlite3.connect('database/hafez.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    """صفحه اصلی"""
    return render_template('index.html')

@app.route('/get_fal')
def get_fal():
    """API گرفتن فال تصادفی"""
    conn = get_db_connection()
    
    # تعداد کل غزل‌ها
    cursor = conn.execute('SELECT COUNT(*) FROM ghazals')
    total_ghazals = cursor.fetchone()[0]
    
    if total_ghazals == 0:
        conn.close()
        return jsonify({'error': 'هیچ غزلی در دیتابیس نیست'}), 404
    
    # انتخاب تصادفی
    random_offset = random.randint(0, total_ghazals - 1)
    
    # گرفتن غزل تصادفی
    cursor = conn.execute('SELECT * FROM ghazals ORDER BY number LIMIT 1 OFFSET ?', (random_offset,))
    ghazal = cursor.fetchone()
    
    conn.close()
    
    if ghazal:
        return jsonify({
            'number': ghazal['number'],
            'title': ghazal['title'],
            'text': ghazal['text'],
            'verse_count': ghazal['verse_count'],
            'audio_url': f'/static/audio/{ghazal["audio_file"]}',
            'ganjoor_url': ghazal['ganjoor_url'],
            'interpretation': f'این غزل {ghazal["verse_count"]} بیت دارد و از شاهکارهای حافظ شیرازی است که در موضوع عرفان و عشق سروده شده.'
        })
    else:
        return jsonify({'error': 'غزل پیدا نشد'}), 404

@app.route('/get_ghazal/<int:number>')
def get_specific_ghazal(number):
    """دریافت غزل خاص با شماره"""
    if not (1 <= number <= 495):
        return jsonify({'error': 'شماره غزل باید بین 1 تا 495 باشد'}), 400
    
    conn = get_db_connection()
    
    cursor = conn.execute('SELECT * FROM ghazals WHERE number = ?', (number,))
    ghazal = cursor.fetchone()
    
    conn.close()
    
    if ghazal:
        return jsonify({
            'number': ghazal['number'],
            'title': ghazal['title'],
            'text': ghazal['text'],
            'verse_count': ghazal['verse_count'],
            'audio_url': f'/static/audio/{ghazal["audio_file"]}',
            'ganjoor_url': ghazal['ganjoor_url'],
            'interpretation': f'غزل شماره {number} از دیوان حافظ شیرازی'
        })
    else:
        return jsonify({'error': f'غزل شماره {number} در دیتابیس یافت نشد'}), 404

@app.route('/search')
def search_ghazals():
    """جستجو در غزل‌ها"""
    query = request.args.get('q', '').strip()
    
    if not query:
        return jsonify({'error': 'متن جستجو خالی است'}), 400
    
    conn = get_db_connection()
    
    # جستجو در عنوان و متن
    cursor = conn.execute(
        'SELECT number, title, text FROM ghazals WHERE title LIKE ? OR text LIKE ? LIMIT 20',
        (f'%{query}%', f'%{query}%')
    )
    
    results = []
    for row in cursor.fetchall():
        results.append({
            'number': row['number'],
            'title': row['title'],
            'preview': row['text'][:100] + '...' if len(row['text']) > 100 else row['text']
        })
    
    conn.close()
    
    return jsonify({
        'query': query,
        'results': results,
        'count': len(results)
    })

@app.route('/stats')
def stats():
    """آمار دیتابیس"""
    conn = get_db_connection()
    
    # تعداد کل غزل‌ها
    cursor = conn.execute('SELECT COUNT(*) FROM ghazals')
    total = cursor.fetchone()[0]
    
    # میانگین تعداد ابیات
    cursor = conn.execute('SELECT AVG(verse_count) FROM ghazals WHERE verse_count IS NOT NULL')
    avg_verses = cursor.fetchone()[0] or 0
    
    # آخرین غزل اضافه شده
    cursor = conn.execute('SELECT number, title FROM ghazals ORDER BY created_at DESC LIMIT 1')
    latest = cursor.fetchone()
    
    conn.close()
    
    return jsonify({
        'total_ghazals': total,
        'average_verses': round(avg_verses, 1),
        'latest_ghazal': {
            'number': latest['number'] if latest else None,
            'title': latest['title'] if latest else None
        }
    })

@app.route('/random_numbers')
def random_numbers():
    """لیست اعداد تصادفی برای فال"""
    numbers = [random.randint(1, 495) for _ in range(10)]
    return jsonify({'numbers': numbers})

@app.route('/get_ai_interpretation', methods=['POST'])
def get_ai_interpretation():
    """دریافت تفسیر از دیتابیس"""
    try:
        data = request.json
        ghazal_number = data.get('number', 0)
        interpretation_type = data.get('type', 'fal')
        
        conn = sqlite3.connect('database/hafez.db')
        cursor = conn.cursor()
        
        # جستجو در دیتابیس
        cursor.execute('''
            SELECT i.interpretation, i.source 
            FROM interpretations i
            JOIN ghazals g ON i.ghazal_id = g.id
            WHERE g.number = ? AND i.interpretation_type = ?
        ''', (ghazal_number, interpretation_type))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            interpretation, source = result
            return jsonify({
                'success': True,
                'interpretation': interpretation,
                'source': f'database-{source}'
            })
        else:
            # اگه تو دیتابیس نبود، تفسیر پیش‌فرض
            from utils.ai_helper import get_fallback_interpretation
            fallback = get_fallback_interpretation("", ghazal_number)
            return jsonify({
                'success': True,
                'interpretation': fallback,
                'source': 'fallback'
            })
            
    except Exception as e:
        # در صورت خطا، fallback
        from utils.ai_helper import get_fallback_interpretation
        fallback = get_fallback_interpretation("", ghazal_number)
        return jsonify({
            'success': True,
            'interpretation': fallback,
            'source': 'error-fallback'
        })

@app.errorhandler(404)
def not_found(error):
    """خطای 404"""
    return jsonify({'error': 'صفحه یافت نشد'}), 404

@app.errorhandler(500)
def internal_error(error):
    """خطای 500"""
    return jsonify({'error': 'خطای سرور'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)