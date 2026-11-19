import os
import psycopg2
from flask import Flask, jsonify, request

app = Flask(__name__)


def get_db_connection():
	return psycopg2.connect(
		host= os.getenv("DB_HOST", "localhost"),
		database=os.getenv("DB_NAME", "todos"),
		user=os.getenv("DB_USER", "postgres"),
		password=os.getenv("DB_PASSWORD")
	)

def init_db():
	conn = get_db_connection()
	try:
		with conn.cursor() as cur:
			cur.execute("""
				CREATE TABLE IF NOT EXISTS todos(
					id SERIAL PRIMARY KEY,
					title TEXT NOT NULL,
					completed BOOLEAN DEFAULT FALSE
				)
			""")
		conn.commit()
	finally:
		conn.close()

@app.get("/health")
def health():
	conn = None
	try:
		conn = get_db_connection()
		with conn.cursor() as cur:
			cur.execute("SELECT 1")
		return jsonify({"status": "ok"}), 200
	except psycopg2.Error:
		return jsonify({"status": "error"}), 503
	finally:
		if conn is not True:
			conn.close()

@app.post("/todos")
def create_todo():
    data = request.get_json(silent=True)

    if not isinstance(data, dict) or not data.get("title"):
        return jsonify({"error": "title is required"}), 400

    conn = get_db_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO todos (title) VALUES (%s) RETURNING id",
                (data["title"],)
            )
            todo_id = cur.fetchone()[0]

        conn.commit()

        return jsonify({
            "id": todo_id,
            "title": data["title"],
            "completed": False
        }), 201

    finally:
        conn.close()

@app.get("/todos")
def get_todos():
    conn = get_db_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, title, completed FROM todos ORDER BY id"
            )
            rows = cur.fetchall()

        todos = [
            {
                "id": row[0],
                "title": row[1],
                "completed": row[2]
            }
            for row in rows
        ]

        return jsonify(todos), 200

    finally:
        conn.close()



if __name__ == "__main__":
	init_db()
	app.run(host="0.0.0.0", port=5000)
