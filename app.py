# -*- coding: utf-8 -*-
"""
app.py  –  حافظ‌خوانی (Flask API)
"""
import random, sqlite3
from contextlib import closing

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


# ------------------------------------------------------------------ #
#  روت‌های وب
# ------------------------------------------------------------------ #
@app.route("/")
def index():
    """صفحهٔ اصلی (قالب Jinja)"""
    return render_template("index.html")


@app.route("/get_ghazal/<int:number>")
def get_ghazal(number: int):
    if not 1 <= number <= 495:
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
        return jsonify(error="غزل پیدا نشد"), 404

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
    خروجی:
    {
      "query":"فسوس",
      "count":2,
      "results":[
        {"number":123, "match":"فسوس كه ..."},
        ...
      ]
    }
    """
    query = request.args.get("q", "").strip()
    if not query:
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

    return jsonify(query=query, count=len(results), results=results)


# ------------------------------------------------------------------ #
#  (اختیاری) غزل تصادفی + AI
# ------------------------------------------------------------------ #
@app.route("/get_fal")
def get_fal():
    """غزل تصادفی (در صورت نیاز)"""
    with get_db() as conn, closing(conn.cursor()) as cur:
        cur.execute("SELECT COUNT(*) FROM ghazals")
        total = cur.fetchone()[0]
        cur.execute("SELECT * FROM ghazals ORDER BY RANDOM() LIMIT 1")
        gh = cur.fetchone()

    if not gh:
        return jsonify(error="غزل موجود نیست"), 404

    return jsonify(
        number=gh["number"],
        title=gh["title"],
        text=gh["text"],
        interpretation=""
    )


# ------------------------------------------------------------------ #
#  خطاها
# ------------------------------------------------------------------ #
@app.errorhandler(404)
def not_found(_):
    return jsonify(error="صفحه یافت نشد"), 404


@app.errorhandler(500)
def server_error(_):
    return jsonify(error="خطای سرور"), 500


# ------------------------------------------------------------------ #

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)