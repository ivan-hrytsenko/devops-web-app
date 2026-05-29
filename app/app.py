#!/usr/bin/env python3
import argparse
import os
from flask import Flask, request, jsonify, Response
import db

parser = argparse.ArgumentParser()
parser.add_argument('--host', default=os.environ.get('APP_HOST', '127.0.0.1'))
parser.add_argument('--port', type=int, default=int(os.environ.get('APP_PORT', 5000)))
parser.add_argument('--db-host', default=os.environ.get('DB_HOST', '127.0.0.1'))
parser.add_argument('--db-port', type=int, default=int(os.environ.get('DB_PORT', 3306)))
parser.add_argument('--db-user', default=os.environ.get('DB_USER', ''))
parser.add_argument('--db-password', default=os.environ.get('DB_PASSWORD', ''))
parser.add_argument('--db-name', default=os.environ.get('DB_NAME', ''))
args, _ = parser.parse_known_args()

conn = None
db_ready = False
db_error = 'not initialized'

try:
    conn = db.get_connection(
        args.db_host, args.db_port,
        args.db_user, args.db_password, args.db_name
    )
    db_ready = True
    db_error = ''
except Exception as e:
    db_error = str(e)

app = Flask(__name__)


@app.route('/health/alive')
def alive():
    return Response('OK', status=200)


@app.route('/health/ready')
def ready():
    if db_ready:
        return Response('OK', status=200)
    return Response(f'DB not available: {db_error}', status=500)


@app.route('/')
def index():
    accept = request.headers.get('Accept', '')
    if 'text/html' not in accept and '*/*' not in accept:
        return Response('Not Acceptable', status=406)
    html = """<html><body>
    <h1>Task Tracker API</h1>
    <ul>
      <li>GET /tasks</li>
      <li>POST /tasks</li>
      <li>POST /tasks/&lt;id&gt;/done</li>
    </ul>
    </body></html>"""
    return Response(html, content_type='text/html')


def respond(data, html_fn):
    accept = request.headers.get('Accept', '')
    if 'text/html' in accept:
        return Response(html_fn(data), content_type='text/html')
    return jsonify(data)


@app.route('/tasks', methods=['GET'])
def get_tasks():
    with conn.cursor() as cursor:
        cursor.execute("SELECT id, title, status, created_at FROM tasks")
        tasks = cursor.fetchall()
    for t in tasks:
        if hasattr(t['created_at'], 'isoformat'):
            t['created_at'] = t['created_at'].isoformat()

    def to_html(data):
        rows = ''.join(
            f"<tr><td>{t['id']}</td><td>{t['title']}</td>"
            f"<td>{t['status']}</td><td>{t['created_at']}</td></tr>"
            for t in data
        )
        return (
            "<html><body>"
            "<table border='1'>"
            "<tr><th>id</th><th>title</th><th>status</th><th>created_at</th></tr>"
            f"{rows}"
            "</table></body></html>"
        )

    return respond(tasks, to_html)


@app.route('/tasks', methods=['POST'])
def create_task():
    data = request.get_json(force=True)
    title = data.get('title', '').strip()
    if not title:
        return jsonify({'error': 'title is required'}), 400
    with conn.cursor() as cursor:
        cursor.execute("INSERT INTO tasks (title) VALUES (%s)", (title,))
        conn.commit()
        task_id = cursor.lastrowid
        cursor.execute(
            "SELECT id, title, status, created_at FROM tasks WHERE id=%s",
            (task_id,)
        )
        task = cursor.fetchone()
    if hasattr(task['created_at'], 'isoformat'):
        task['created_at'] = task['created_at'].isoformat()
    return jsonify(task), 201


@app.route('/tasks/<int:task_id>/done', methods=['POST'])
def mark_done(task_id):
    with conn.cursor() as cursor:
        cursor.execute(
            "UPDATE tasks SET status='done' WHERE id=%s", (task_id,)
        )
        conn.commit()
        if cursor.rowcount == 0:
            return jsonify({'error': 'not found'}), 404
        cursor.execute(
            "SELECT id, title, status, created_at FROM tasks WHERE id=%s",
            (task_id,)
        )
        task = cursor.fetchone()
    if hasattr(task['created_at'], 'isoformat'):
        task['created_at'] = task['created_at'].isoformat()
    return jsonify(task)


if __name__ == '__main__':
    app.run(host=args.host, port=args.port)