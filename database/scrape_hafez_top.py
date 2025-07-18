# -*- coding: utf-8 -*-
"""
استخراج تفسیر غزل‌های hafez.top  (تابع جدید  extract_interpretation)
"""

import re, time, sqlite3, requests
from pathlib import Path
from bs4 import BeautifulSoup

DB_PATH   = Path(__file__).resolve().parents[1] / "database" / "hafez.db"
URL_TPL   = "https://hafez.top/ghazal-{}/"
HEADERS   = {"User-Agent": "Mozilla/5.0 (HafezScraper 1.1)"}


# ------------------------------------------------------------------
def extract_interpretation(html:str) -> str:
    """برمی‌گرداند متن تفسیر، یا رشتهٔ خالی اگر پیدا نشد"""
    soup = BeautifulSoup(html, "html.parser")

    # 1) تیترِ «معنی و تفسیر غزل» را پیدا کن
    title_tag = None
    for tag in soup.find_all(re.compile(r"h\d")):        # h1, h2, h3 ...
        if tag.get_text(strip=True).startswith("معنی و تفسیر غزل"):
            title_tag = tag
            break
    if not title_tag:
        return ""

    # 2) از برادر بعدی تا قبل از هدینگ بعدی، پاراگراف‌ها را جمع کن
    collected = []
    for sib in title_tag.find_next_siblings():
        if re.match(r"h\d", sib.name):          # رسیدیم به هدینگ بعدی، توقف
            break
        if sib.name == "p":
            txt = sib.get_text(" ", strip=True)
            if txt:
                collected.append(txt)

    return "\n".join(collected).strip()
# ------------------------------------------------------------------


def already(conn, num):
    cur = conn.execute("""
        SELECT EXISTS(
            SELECT 1 FROM interpretations
             WHERE ghazal_id=(SELECT id FROM ghazals WHERE number=?)
               AND interpretation_type='verse')
    """, (num,))
    return cur.fetchone()[0]

def save(conn, num, text):
    cur = conn.execute("SELECT id FROM ghazals WHERE number=?", (num,))
    row = cur.fetchone()
    if not row:
        print(f"   ❌ غزل {num} در جدول ghazals نیست")
        return False
    conn.execute("""
        INSERT INTO interpretations
               (ghazal_id,interpretation_type,interpretation,source)
        VALUES (?,?,?,?)
    """, (row["id"], "verse", text, "hafez.top"))
    conn.commit(); return True

def run():
    conn = sqlite3.connect(DB_PATH); conn.row_factory = sqlite3.Row
    for n in range(1, 496):
        if already(conn, n):
            print(f"⏭  {n}: موجود است"); continue
        print(f"🔎  {n}: ", end="", flush=True)

        try:
            r = requests.get(URL_TPL.format(n), headers=HEADERS, timeout=15)
        except Exception as e:
            print("⛔ error", e); continue

        if r.status_code != 200:
            print(f"HTTP {r.status_code}"); continue

        text = extract_interpretation(r.text)
        if not text:
            print("بدون تفسیر"); continue

        print("… ذخیره", "✔" if save(conn, n, text) else "❌")
        time.sleep(1.0)

    conn.close(); print("پایان.")

if __name__ == "__main__":
    run()