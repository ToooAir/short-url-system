from flask import Flask, request, jsonify, redirect
import sqlite3
from urllib.parse import urlparse
import string
import random
import time
from functools import wraps

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

# 資料庫初始化
def init_db():
    conn = sqlite3.connect('urls.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS urls
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  original_url TEXT NOT NULL,
                  short_code TEXT NOT NULL UNIQUE,
                  expiration_date INTEGER NOT NULL)''')
    conn.commit()
    conn.close()

init_db()

# 產生短網址代碼
def generate_short_code():
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(6))

# URL 驗證
def is_valid_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False

# 速率限制裝飾器
def rate_limit(limit=10, per=60):
    def decorator(f):
        last_reset = time.time()
        calls = 0
        @wraps(f)
        def decorated_function(*args, **kwargs):
            nonlocal last_reset, calls
            now = time.time()
            if now - last_reset > per:
                calls = 0
                last_reset = now
            calls += 1
            if calls > limit:
                return jsonify({"success": False, "reason": "超過速率限制"}), 429
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@app.route('/')
def home():
    return "短網址系統正在運行！"

# 建立短網址 API
@app.route('/shorten', methods=['POST'])
@rate_limit()
def create_short_url():
    data = request.json
    original_url = data.get('original_url')

    if not original_url:
        return jsonify({"success": False, "reason": "缺少 original_url"}), 400

    if len(original_url) > 2048:
        return jsonify({"success": False, "reason": "URL 過長"}), 400

    if not is_valid_url(original_url):
        return jsonify({"success": False, "reason": "無效的 URL"}), 400

    short_code = generate_short_code()
    expiration_date = int(time.time()) + 30 * 24 * 60 * 60  # 30 天後

    conn = sqlite3.connect('urls.db')
    c = conn.cursor()
    c.execute("INSERT INTO urls (original_url, short_code, expiration_date) VALUES (?, ?, ?)",
              (original_url, short_code, expiration_date))
    conn.commit()
    conn.close()

    short_url = f"http://{request.host}/{short_code}"
    return jsonify({
        "short_url": short_url,
        "expiration_date": expiration_date,
        "success": True
    }), 201

# 重新導向 API
@app.route('/<short_code>')
def redirect_to_original(short_code):
    conn = sqlite3.connect('urls.db')
    c = conn.cursor()
    c.execute("SELECT original_url, expiration_date FROM urls WHERE short_code = ?", (short_code,))
    result = c.fetchone()
    conn.close()

    if result is None:
        return jsonify({"success": False, "reason": "找不到短網址"}), 404

    original_url, expiration_date = result
    if int(time.time()) > expiration_date:
        return jsonify({"success": False, "reason": "短網址已過期"}), 410

    return redirect(original_url, 302)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)