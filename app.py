from flask import Flask, request, render_template, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Замени на более безопасный ключ в реальном проекте

# Настройка Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Настройка Flask-SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# Модель пользователя
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)  # Храним пароль в хэше (в реальном проекте используй bcrypt)


# Модель задачи
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    author = db.relationship('User', backref=db.backref('tasks', lazy=True))


# Загрузка пользователя для Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Создание базы данных
with app.app_context():
    db.create_all()


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password'].strip()
        if not username or not password:
            flash('Пожалуйста, заполните оба поля!')
            return redirect(url_for('register'))
        if User.query.filter_by(username=username).first():
            flash('Этот пользователь уже существует!')
            return redirect(url_for('register'))
        user = User(username=username, password=password)  # В реальном проекте хэшируй пароль
        db.session.add(user)
        db.session.commit()
        flash('Регистрация успешна! Войдите, чтобы продолжить.')
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password'].strip()
        user = User.query.filter_by(username=username, password=password).first()
        if user and user.password == password:  # В реальном проекте используй хэширование
            login_user(user)
            return redirect(url_for('index'))
        flash('Неверное имя пользователя или пароль!')
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    if request.method == 'POST':
        task = request.form['task'].strip()
        if not task:
            flash('Пожалуйста, введите задачу!')
            return redirect(url_for('index'))
        new_task = Task(task=task, author_id=current_user.id)
        db.session.add(new_task)
        db.session.commit()
        flash('Задача добавлена!')
        return redirect(url_for('index'))

    tasks = Task.query.filter_by(author_id=current_user.id).order_by(Task.created_at.desc()).all()
    return render_template('index.html', tasks=tasks)


@app.route('/delete/<int:task_id>')
@login_required
def delete(task_id):
    task = Task.query.get_or_404(task_id)
    if task.author_id != current_user.id:
        flash('У вас нет прав для удаления этой задачи!')
        return redirect(url_for('index'))
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for('index'))


@app.route('/edit/<int:task_id>', methods=['GET', 'POST'])
@login_required
def edit(task_id):
    task = Task.query.get_or_404(task_id)
    if task.author_id != current_user.id:
        flash('У вас нет прав для редактирования этой задачи!')
        return redirect(url_for('index'))

    if request.method == 'POST':
        task.task = request.form['task'].strip()
        if not task.task:
            flash('Пожалуйста, введите задачу!')
            return redirect(url_for('edit', task_id=task_id))
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('edit.html', task=task)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)