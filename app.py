# -*- coding: utf-8 -*-
"""
app.py  –  حافظ‌خوانی (Flask API) با سیستم لاگ
"""
import random, sqlite3
from contextlib import closing
from datetime import datetime

from flask import Flask, render_template, jsonify, request, current_app

# ------------------------------------------------------------------ #
#  تنظیمات پایه
# ------------------------------------------------------------------ #
class Config:
    SECRET_KEY = "hafez-secret"
    DATABASE_PATH = "database/hafez.db"
    JSON_AS_ASCII = False          # برای ارسال UTF-8 واقعی


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
    """ثبت عملیات کاربران"""
    try:
        ip = request.remote_addr or 'Unknown'
        user_agent = request.headers.get('User-Agent', 'Unknown')
        referer = request.headers.get('Referer', '')
        page_url = request.url
        
        with get_db() as conn:
            conn.execute("""
                INSERT INTO user_logs 
                (ip_address, user_agent, action_type, ghazal_number, search_query, referer, page_url)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                ip, user_agent, action_type,
                kwargs.get('ghazal_number'),
                kwargs.get('search_query'),
                referer, page_url
            ))
            conn.commit()
    except Exception as e:
        print(f"❌ Log error: {e}")


# ------------------------------------------------------------------ #
#  روت‌های وب
# ------------------------------------------------------------------ #
@app.route("/")
def index():
    """صفحهٔ اصلی (قالب Jinja)"""
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

    # ✅ ثبت لاگ موفق
    log_user_action('ghazal_view', ghazal_number=number)

    return jsonify(
        number=row["number"],
        title=row["title"],
        text=row["text"],
        interpretation=row["interpretation"] or ""
    )


@app.route("/search")
def search_ghazals():
    """
    جستجو در متن یا عنوان غزل‌ها و برگرداندن مصرعی که عبارت در آن پیدا شده
    """
    query = request.args.get("q", "").strip()
    if not query:
        log_user_action('empty_search')
        return jsonify(error="متن جستجو خالی است"), 400

    like = f"%{query}%"

    with get_db() as conn, closing(conn.cursor()) as cur:
        cur.execute("""
            SELECT number, title, text
              FROM ghazals
             WHERE text  LIKE ?
                OR title LIKE ?
             LIMIT 20
        """, (like, like))
        rows = cur.fetchall()

    results = []
    for r in rows:
        match_line = ""
        # جستجو در هر مصرع
        for line in r["text"].split("\n"):
            if query in line:
                match_line = line.strip()
                break
        # اگر در متن نبود از عنوان کمک می‌گیریم
        if not match_line:
            match_line = r["title"].split("\n")[0]

        results.append({"number": r["number"], "match": match_line})

    # ✅ ثبت لاگ جستجو
    log_user_action('search', search_query=query, results_count=len(results))

    return jsonify(query=query, count=len(results), results=results)


@app.route("/get_fal")
def get_fal():
    """غزل تصادفی (فال)"""
    with get_db() as conn, closing(conn.cursor()) as cur:
        cur.execute("SELECT COUNT(*) FROM ghazals")
        total = cur.fetchone()[0]
        cur.execute("SELECT * FROM ghazals ORDER BY RANDOM() LIMIT 1")
        gh = cur.fetchone()

    if not gh:
        log_user_action('fal_error')
        return jsonify(error="غزل موجود نیست"), 404

    # ✅ ثبت لاگ فال
    log_user_action('fal_request', ghazal_number=gh["number"])

    return jsonify(
        number=gh["number"],
        title=gh["title"],
        text=gh["text"],
        interpretation=""
    )


# ------------------------------------------------------------------ #
#  آمار و گزارشات (جدید)
# ------------------------------------------------------------------ #
@app.route("/admin/stats")
def get_stats():
    """آمار کلی سایت - فقط برای ادمین"""
    try:
        with get_db() as conn, closing(conn.cursor()) as cur:
            # آمار کلی
            cur.execute("SELECT COUNT(*) FROM user_logs")
            total_requests = cur.fetchone()[0]
            
            # آمار امروز
            cur.execute("""
                SELECT COUNT(*) FROM user_logs 
                WHERE date(timestamp) = date('now')
            """)
            today_requests = cur.fetchone()[0]
            
            # محبوب‌ترین غزل‌ها
            cur.execute("""
                SELECT ghazal_number, COUNT(*) as count 
                FROM user_logs 
                WHERE action_type = 'ghazal_view' AND ghazal_number IS NOT NULL
                GROUP BY ghazal_number 
                ORDER BY count DESC 
                LIMIT 10
            """)
            popular_ghazals = [{"number": row[0], "views": row[1]} for row in cur.fetchall()]
            
            # آمار جستجو
            cur.execute("""
                SELECT search_query, COUNT(*) as count 
                FROM user_logs 
                WHERE action_type = 'search' AND search_query IS NOT NULL
                GROUP BY search_query 
                ORDER BY count DESC 
                LIMIT 10
            """)
            popular_searches = [{"query": row[0], "count": row[1]} for row in cur.fetchall()]

        return jsonify({
            "total_requests": total_requests,
            "today_requests": today_requests,
            "popular_ghazals": popular_ghazals,
            "popular_searches": popular_searches
        })
    except Exception as e:
        return jsonify(error=f"خطا در دریافت آمار: {str(e)}"), 500


# ------------------------------------------------------------------ #
#  خطاها
# ------------------------------------------------------------------ #
@app.errorhandler(404)
def not_found(_):
    log_user_action('404_error')
    return jsonify(error="صفحه یافت نشد"), 404


@app.errorhandler(500)
def server_error(_):
    log_user_action('500_error')
    return jsonify(error="خطای سرور"), 500


# ------------------------------------------------------------------ #

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)