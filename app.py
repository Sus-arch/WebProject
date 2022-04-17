import flask_login
from flask import Flask, render_template, redirect, make_response, jsonify, request
from data import db_session, posts_api
from data.users import User
from data.posts import Post
from data.comments import Comment
from flask_login import LoginManager, login_user, logout_user, login_required
from forms.user import RegisterForm, LoginForm, EditForm
from forms.post import AddForm, EditPostForm
from forms.comment import AddCommentForm
import os
from waitress import serve
from utils.file_reader import get_text


app = Flask(__name__)
app.config['SECRET_KEY'] = 'NJwadok12LMKF3KMlmcd232v_key'
# URL = os.environ.get('DATABASE_URL').replace("postgres://", "postgresql+psycopg2://", 1)
login_manager = LoginManager()
login_manager.init_app(app)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        if db_sess.query(User).filter(User.nick == form.nick.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пользователь с таким ником уже зарегистрирован")
        user = User(
            name=form.name.data,
            email=form.email.data,
            nick=form.nick.data,
            about=form.about.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/', methods=['GET', 'POST'])
def base_site():
    db_sess = db_session.create_session()
    posts = db_sess.query(Post).all()
    comments = db_sess.query(Comment).all()
    form = AddCommentForm()
    if form.validate_on_submit():
        comment = Comment(
            text=form.text.data,
            main_post=form.main_post.data,
            creater_id=flask_login.current_user.id
        )
        db_sess.add(comment)
        db_sess.commit()
        return redirect('/')
    return render_template('index.html', posts=posts[::-1], comments=comments, title='Twitterus', form=form)


@app.route('/user/<int:user_id>', methods=['GET', 'POST'])
def get_user(user_id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).get(user_id)
    if user:
        all_post = db_sess.query(Post).filter(Post.creater_id == user_id)
        comments = db_sess.query(Comment).all()
        form = AddCommentForm()
        if form.validate_on_submit():
            comment = Comment(
                text=form.text.data,
                main_post=form.main_post.data,
                creater_id=flask_login.current_user.id
            )
            db_sess.add(comment)
            db_sess.commit()
            return redirect(f'/user/{user_id}')
        return render_template('user.html', title=user.nick, name=user.name, about=user.about, posts=all_post, id=user_id, comments=comments, form=form)
    return jsonify({'error': 'user not found'})


@app.route('/edit/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).get(user_id)
    form = EditForm()
    if not user:
        return jsonify({'error': 'user not found'})
    if not flask_login.current_user.is_authenticated or flask_login.current_user.id != user.id:
        return jsonify({'error': 'access denied'})
    if form.validate_on_submit():
        if db_sess.query(User).filter(User.nick == form.nick.data).first() and user.nick != form.nick.data:
            return render_template('edit.html', title='Регистрация',
                                   form=form,
                                   message="Пользователь с таким ником уже зарегистрирован")
        user.name = form.name.data
        user.nick = form.nick.data
        user.about = form.about.data

        db_sess.commit()
        return redirect('/')
    form.name.data = user.name
    form.nick.data = user.nick
    form.about.data = user.about
    return render_template('edit.html', title='Изменить профиль', form=form)


@app.route('/add_post', methods=['GET', 'POST'])
def add_post():
    form = AddForm()
    if not flask_login.current_user.is_authenticated:
        return jsonify({'error': 'not logged in'})
    if form.validate_on_submit():
        if not form.text.data and not request.files['file']:
            return render_template('add_post.html', title='Добавить пост',
                                   form=form, message='Нельзя создать пост без текста')
        text = ''
        if form.text.data:
            text = form.text.data + '\n'
        if request.files['file']:
            file = request.files['file']
            path = os.path.join('uploads', file.filename)
            file.save(path)
            text += get_text(path)
            if not text:
                return render_template('add_post.html', title='Добавить пост',
                                       form=form, message='Некорректный файл')
            os.remove(path)
        post = Post(
            title=form.title.data,
            creater_id=flask_login.current_user.id,
            text=text
        )
        db_sess = db_session.create_session()
        db_sess.add(post)
        db_sess.commit()
        return redirect('/')
    return render_template('add_post.html', title='Добавить пост', form=form)


@app.route('/edit_post/<int:post_id>', methods=['GET', 'POST'])
def edit_post(post_id):
    db_sess = db_session.create_session()
    form = EditPostForm()
    post = db_sess.query(Post).get(post_id)
    if not post:
        return jsonify({'error': 'post not found'})
    if not flask_login.current_user.is_authenticated or flask_login.current_user.id != post.creater_id:
        return jsonify({'error': 'access denied'})
    if form.validate_on_submit():
        post.title = form.title.data
        post.text = form.text.data
        db_sess.commit()
        return redirect(f'/user/{post.creater_id}')
    form.title.data = post.title
    form.text.data = post.text
    return render_template('edit_post.html', title='Изменить пост', form=form)


@app.route('/delete_post/<int:post_id>/<int:page>', methods=['GET', 'POST'])
def delete_post(post_id, page):
    db_sess = db_session.create_session()
    post = db_sess.query(Post).get(post_id)
    if not post:
        return jsonify({'error': 'post not found'})
    if not flask_login.current_user.is_authenticated or flask_login.current_user.id != post.creater_id:
        return jsonify({'error': 'access denied'})
    db_sess.delete(post)
    db_sess.commit()
    if page == 1:
        return redirect('/')
    elif page == 2:
        return redirect(f'/user/{post.creater_id}')


@app.route('/comment/delete/<int:com_id>/<int:page>', methods=['GET', 'POST'])
def delete_comment(com_id, page):
    db_sess = db_session.create_session()
    com = db_sess.query(Comment).get(com_id)
    if not com:
        return jsonify({'error': 'comment not found'})
    if not flask_login.current_user.is_authenticated or flask_login.current_user.id != com.creater_id:
        return jsonify({'error': 'access denied'})
    db_sess.delete(com)
    db_sess.commit()
    if page == 1:
        return redirect('/')
    elif page == 2:
        main_post = db_sess.query(Post).get(com.main_post)
        return redirect(f"/user/{main_post.creater_id}")


def main():
    db_session.global_init('db/blogs.db')
    # db_session.global_init(URL)
    app.register_blueprint(posts_api.blueprint)
    port = int(os.environ.get("PORT", 5000))
    app.run(port=port, host='0.0.0.0')
    # serve(app, port=port, host='0.0.0.0')


if __name__ == '__main__':
    main()
