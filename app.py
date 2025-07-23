# -*- coding: utf-8 -*-
"""
app.py  –  حافظ‌خوانی (Flask API) با سیستم analytics کامل
"""
import random, sqlite3
from contextlib import closing
from datetime import datetime

from flask import Flask, render_template, jsonify, request, current_app, session
from utils.analytics_helper import detect_device_info, get_location_from_ip, generate_session_id

# ------------------------------------------------------------------ #
#  تنظیمات پایه
# ------------------------------------------------------------------ #
class Config:
    SECRET_KEY = "hafez-secret-key-2025"
    DATABASE_PATH = "database/hafez.db" 
    JSON_AS_ASCII = False


app = Flask(__name__)
app.config.from_object(Config)


# ------------------------------------------------------------------ #
#  ابزار پایگاه داده
# ------------------------------------------------------------------ #
def get_db():
    db_path = current_app.config["DATABASE_PATH"]
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def log_user_action(action_type, **kwargs):
    """ثبت کامل عملیات کاربران با analytics"""
    try:
        # اطلاعات پایه
        ip = request.remote_addr or 'Unknown'
        user_agent = request.headers.get('User-Agent', 'Unknown')
        referer = request.headers.get('Referer', '')
        page_url = request.url
        
        # Session tracking
        if 'session_id' not in session:
            session['session_id'] = generate_session_id()
        session_id = session['session_id']
        
        # Device detection
        device_info = detect_device_info(user_agent)
        
        # Geographic info
        location_info = get_location_from_ip(ip)
        
        with get_db() as conn:
            conn.execute("""
                INSERT INTO user_logs 
                (ip_address, user_agent, action_type, ghazal_number, search_query, 
                 referer, page_url, device_type, browser, os, country, city, region, session_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                ip, user_agent, action_type,
                kwargs.get('ghazal_number'),
                kwargs.get('search_query'),
                referer, page_url,
                device_info['device_type'],
                device_info['browser'], 
                device_info['os'],
                location_info['country'],
                location_info['city'],
                location_info['region'],
                session_id
            ))
            conn.commit()
    except Exception as e:
        print(f"❌ Log error: {e}")


# ------------------------------------------------------------------ #
#  باقی کد مثل قبل... (همون route های قبلی)
# ------------------------------------------------------------------ #
@app.route("/")
def index():
    log_user_action('page_visit', page='index')
    return render_template("index.html")

@app.route("/get_ghazal/<int:number>")
def get_ghazal(number: int):
    if not 1 <= number <= 495:
        log_user_action('invalid_ghazal_request', ghazal_number=number)
        return jsonify(error="شماره باید بین 1 تا 495 باشد"), 400

    with get_db() as conn, closing(conn.cursor()) as cur:
        cur.execute("""
            SELECT g.id, g.number, g.title, g.text,
                   i.interpretation
              FROM ghazals g
         LEFT JOIN interpretations i
                ON i.ghazal_id = g.id AND i.interpretation_type = 'verse'
             WHERE g.number = ?
             LIMIT 1
        """, (number,))
        row = cur.fetchone()

    if not row:
        log_user_action('ghazal_not_found', ghazal_number=number)
        return jsonify(error="غزل پیدا نشد"), 404

    log_user_action('ghazal_view', ghazal_number=number)
    return jsonify(
        number=row["number"],
        title=row["title"],
        text=row["text"],
        interpretation=row["interpretation"] or ""
    )

@app.route("/search")
def search_ghazals():
    query = request.args.get("q", "").strip()
    if not query:
        log_user_action('empty_search')
        return jsonify(error="متن جستجو خالی است"), 400

    like = f"%{query}%"
    with get_db() as conn, closing(conn.cursor()) as cur:
        cur.execute("""
            SELECT number, title, text
              FROM ghazals
             WHERE text  LIKE ? OR title LIKE ?
             LIMIT 20
        """, (like, like))
        rows = cur.fetchall()

    results = []
    for r in rows:
        match_line = ""
        for line in r["text"].split("\n"):
            if query in line:
                match_line = line.strip()
                break
        if not match_line:
            match_line = r["title"].split("\n")[0]
        results.append({"number": r["number"], "match": match_line})

    log_user_action('search', search_query=query, results_count=len(results))
    return jsonify(query=query, count=len(results), results=results)

@app.route("/get_fal")
def get_fal():
    with get_db() as conn, closing(conn.cursor()) as cur:
        cur.execute("SELECT * FROM ghazals ORDER BY RANDOM() LIMIT 1")
        gh = cur.fetchone()

    if not gh:
        log_user_action('fal_error')
        return jsonify(error="غزل موجود نیست"), 404

    log_user_action('fal_request', ghazal_number=gh["number"])
    return jsonify(
        number=gh["number"],
        title=gh["title"],
        text=gh["text"],
        interpretation=""
    )

@app.route("/admin/stats")
def get_stats():
    """آمار پیشرفته سایت"""
    try:
        with get_db() as conn, closing(conn.cursor()) as cur:
            stats = {}
            
            # آمار کلی
            cur.execute("SELECT COUNT(*) FROM user_logs")
            stats['total_requests'] = cur.fetchone()[0]
            
            cur.execute("SELECT COUNT(DISTINCT session_id) FROM user_logs WHERE session_id IS NOT NULL")
            stats['unique_visitors'] = cur.fetchone()[0]
            
            # آمار امروز
            cur.execute("SELECT COUNT(*) FROM user_logs WHERE date(timestamp) = date('now')")
            stats['today_requests'] = cur.fetchone()[0]
            
            # آمار دستگاه‌ها
            cur.execute("""
                SELECT device_type, COUNT(*) as count 
                FROM user_logs 
                WHERE device_type IS NOT NULL
                GROUP BY device_type
            """)
            stats['devices'] = dict(cur.fetchall())
            
            # آمار کشورها  
            cur.execute("""
                SELECT country, COUNT(*) as count 
                FROM user_logs 
                WHERE country IS NOT NULL AND country != 'Unknown'
                GROUP BY country 
                ORDER BY count DESC 
                LIMIT 10
            """)
            stats['countries'] = dict(cur.fetchall())
            
            # محبوب‌ترین غزل‌ها
            cur.execute("""
                SELECT ghazal_number, COUNT(*) as count 
                FROM user_logs 
                WHERE action_type = 'ghazal_view' AND ghazal_number IS NOT NULL
                GROUP BY ghazal_number 
                ORDER BY count DESC 
                LIMIT 10
            """)
            stats['popular_ghazals'] = [{"number": row[0], "views": row[1]} for row in cur.fetchall()]

        return jsonify(stats)
    except Exception as e:
        return jsonify(error=f"خطا در دریافت آمار: {str(e)}"), 500

@app.errorhandler(404)
def not_found(_):
    log_user_action('404_error')
    return jsonify(error="صفحه یافت نشد"), 404

@app.errorhandler(500)
def server_error(_):
    log_user_action('500_error')
    return jsonify(error="خطای سرور"), 500

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)