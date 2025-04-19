from flask import Flask, render_template, redirect, request, url_for, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from werkzeug.security import generate_password_hash, check_password_hash
import sys
from datetime import datetime

sys.path.append('data_and_db')
from db_setup import User, Post

app = Flask(__name__)
app.config['SECRET_KEY'] = '150708'

engine = create_engine('sqlite:///data_and_db/YumRecipe.db')
Session = sessionmaker(bind=engine)
session = Session()

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'logging'


@login_manager.user_loader
def load_user(user_id):
    return session.query(User).get(int(user_id))  # загружает юзер


@app.route('/')
def mainstr():
    posts = session.query(Post).order_by(Post.created_at.desc()).all()
    return render_template('index.html', posts=posts)  # функция отвечающая за работу главной страницы сайта


@app.route('/AboutUs')
def AboutUs():
    about_us = ('Меня зовут Коля, мне 16. Учусь в яндекс лицее, почти закончил второй год.'
                ' Этот проект я делал около 1 месяца. Результат получился таким каким я хотел чтобы он был.'
                ' Собираюсь продолжать обучаться программированию в других курсах.'
                ' Спасибо за вход на сайт и за прочтение.')
    return render_template('about_us.html', about_us=about_us)  # функция отвечающая за работу страницы "о нас"


@app.route('/logging', methods=['GET', 'POST'])  # функция отвечающая за работу страницы "вход"
def logging():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = session.query(User).filter_by(email=email).first()

        if not user:
            flash('Пользователь с таким email не найден!', 'danger')
            return redirect(url_for('logging'))
        elif not check_password_hash(user.password, password):
            flash('Неверный пароль!', 'danger')
            return redirect(url_for('logging'))
        else:
            login_user(user)
            return redirect(url_for('mainstr'))

    return render_template('log_in.html')


@app.route('/registering', methods=['GET', 'POST'])  # функция отвечающая за работу страницы "регистрация"
def registering():
    if request.method == 'POST':
        nickname = request.form.get('nickname')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirmPassword')

        if not nickname or not email or not password or not confirm_password:
            flash('Заполните все поля!', 'danger')
            return redirect(url_for('registering'))

        existing_user = session.query(User).filter_by(email=email).first()
        if existing_user:
            flash('Этот email уже зарегистрирован!', 'danger')
            return redirect(url_for('registering'))

        existing_nickname = session.query(User).filter_by(nickname=nickname).first()
        if existing_nickname:
            flash('Этот никнейм уже занят!', 'danger')
            return redirect(url_for('registering'))

        if password != confirm_password:
            flash('Пароли не совпадают!', 'danger')
            return redirect(url_for('registering'))

        hashed_password = generate_password_hash(password)
        new_user = User(nickname=nickname, email=email, password=hashed_password)
        session.add(new_user)
        session.commit()

        login_user(new_user)

        return redirect(url_for('mainstr'))

    return render_template('register.html')


@app.route('/CreatePost', methods=['GET', 'POST'])  # функция отвечающая за работу страницы "создать пост"
@app.route('/CreatePost/<int:post_id>', methods=['GET', 'POST'])
@login_required
def CreatePost(post_id=None):
    if post_id:
        post = session.query(Post).filter_by(id=post_id).first()

        if not post or (current_user.nickname != 'admin' and current_user.id != post.user_id):
            flash('Вы не можете редактировать этот пост!', 'danger')
            return redirect(url_for('mainstr'))
    else:
        post = None

    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')

        if not content:
            flash('Пост не может быть пустым!', 'danger')
            return redirect(url_for('CreatePost', post_id=post_id) if post_id else url_for('CreatePost'))

        if not title:
            flash('Заголовок не может быть пустым!', 'danger')
            return redirect(url_for('CreatePost', post_id=post_id) if post_id else url_for('CreatePost'))

        if post_id:
            post.title = title
            post.content = content
            post.edited_at = datetime.now()
            post.is_edited = True
        else:
            new_post = Post(title=title, content=content, user_id=current_user.id)

        if post_id:
            session.commit()
        else:
            session.add(new_post)
            session.commit()

        return redirect(url_for('mainstr'))

    return render_template('create_post.html', post=post)


@app.route('/logout')  # функция отвечающая за выход из аккаунта
@login_required
def logout():
    logout_user()
    return redirect(url_for('mainstr'))


@app.route('/edit_post/<int:post_id>', methods=['GET', 'POST']) # функция отвечающая за изменение выложенного пользователем поста
@login_required
def edit_post(post_id):
    return redirect(url_for('CreatePost', post_id=post_id))


@app.route('/delete_post/<int:post_id>')  # функция отвечающая за удаление созданного пользователем поста
@login_required
def delete_post(post_id):
    post = session.query(Post).filter_by(id=post_id).first()

    if not post:
        flash('Пост не найден!', 'danger')
        return redirect(url_for('mainstr'))

    if current_user.nickname != 'admin' and current_user.id != post.user_id:
        flash('Вы не можете удалить этот пост!', 'danger')
        return redirect(url_for('mainstr'))

    session.delete(post)
    session.commit()
    return redirect(url_for('mainstr'))


@app.route('/ban_user/<int:user_id>')  # функция отвечающая за блокировку аккаунта пользователя
@login_required
def ban_user(user_id):
    if current_user.nickname != 'admin':
        return redirect(url_for('mainstr'))

    user = session.query(User).filter_by(id=user_id).first()
    if not user:
        return redirect(url_for('mainstr'))

    posts = session.query(Post).filter_by(user_id=user_id).all()
    for post in posts:
        session.delete(post)

    session.delete(user)
    session.commit()
    return redirect(url_for('mainstr'))


@app.route('/post_detail/<int:post_id>')  # функция отвечающая за работу кнопки "подробнее" поста
def post_detail(post_id):
    post = session.query(Post).filter_by(id=post_id).first()
    if not post:
        return redirect(url_for('mainstr'))
    return render_template('post_detail.html', post=post)


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
