import os
import time
import pymysql
import requests
from flask import Flask, jsonify

app = Flask(__name__)

# 环境变量读取
DB_HOST = os.environ.get("DB_HOST", "127.0.0.1")
DB_PORT = int(os.environ.get("DB_PORT", "3306"))
DB_USER = os.environ.get("DB_USER", "root")
DB_PASS = os.environ.get("DB_PASS", "")
DB_NAME = os.environ.get("DB_NAME", "db_course")

# group1的api URL：本地=http://host.docker.internal:8081 / Mock=Apifox URL / 大盘=http://backend-base:8081
BASE_INFO_API_URL = os.environ.get("BASE_INFO_API_URL")

FLASK_DEBUG = os.environ.get("FLASK_DEBUG", "false").lower() == "true"


def get_conn():
    max_retries = 10
    for attempt in range(max_retries):
        try:
            return pymysql.connect(
                host=DB_HOST, port=DB_PORT, user=DB_USER,
                password=DB_PASS, database=DB_NAME,
                charset="utf8mb4",
                cursorclass=pymysql.cursors.DictCursor,
                connect_timeout=5,
            )
        except pymysql.OperationalError as e:
            if attempt < max_retries - 1:
                print(f"[DB] 连接失败 ({attempt + 1}/{max_retries}): {e}，3s 后重试...")
                time.sleep(3)
            else:
                raise

# 这里为了简化用代码初始化，实际中可以写成init.sql
def init_db():
    conn = get_conn()
    with conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS schedule (
                    id           INT AUTO_INCREMENT PRIMARY KEY,
                    teacher_id   INT NOT NULL,
                    teacher_name VARCHAR(64),
                    course       VARCHAR(128) NOT NULL,
                    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """)
        conn.commit()
    print("[DB] 排课表初始化完成")


@app.route("/api/course/schedule/<int:teacher_id>")
def create_schedule(teacher_id):
    # 调用group1
    teacher_api = f"{BASE_INFO_API_URL}/api/base/teacher/{teacher_id}"
    try:
        resp = requests.get(teacher_api, timeout=5)
        resp.raise_for_status()
        teacher = resp.json()
    except requests.RequestException as e:
        return jsonify({"error": f"无法获取教师信息: {e}"}), 502

    conn = get_conn()
    with conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO schedule (teacher_id, teacher_name, course) VALUES (%s, %s, %s)",
                (teacher["id"], teacher["name"], "软件工程导论"),
            )
            schedule_id = cur.lastrowid
        conn.commit()

    return jsonify({
        "schedule_id":  schedule_id,
        "teacher_id":   teacher["id"],
        "teacher_name": teacher["name"],
        "course":       "软件工程导论",
        "message":      "排课成功",
    }), 201


@app.route("/api/course/health")
def health():
    return jsonify({"status": "ok", "service": "backend-course"})


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=8082, debug=FLASK_DEBUG)
