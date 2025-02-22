from flask import Flask, request, render_template, redirect, url_for, flash
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Нужен для flash-сообщений

def init_db():
    conn = sqlite3.connect('tasks.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS tasks 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  task TEXT NOT NULL, 
                  created_at TEXT NOT NULL, 
                  author TEXT NOT NULL)''')
    conn.commit()
    conn.close()

@app.route('/', methods=['GET', 'POST'])
def index():
    init_db()
    conn = sqlite3.connect('tasks.db')
    c = conn.cursor()

    if request.method == 'POST':
        try:
            task = request.form['task'].strip()
            author = request.form['author'].strip()
            if not task or not author:
                flash('Пожалуйста, заполните оба поля!')
                return redirect(url_for('index'))
            created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            c.execute("INSERT INTO tasks (task, created_at, author) VALUES (?, ?, ?)", (task, created_at, author))
            conn.commit()
        except KeyError:
            flash('Ошибка: заполните форму правильно!')
            return redirect(url_for('index'))

    c.execute("SELECT * FROM tasks")
    tasks = c.fetchall()
    conn.close()

    return render_template('index.html', tasks=tasks)

@app.route('/delete/<int:task_id>')
def delete(task_id):
    conn = sqlite3.connect('tasks.db')
    c = conn.cursor()
    c.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)