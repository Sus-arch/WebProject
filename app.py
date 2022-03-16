import flask_login
from flask import Flask, render_template, redirect, make_response, jsonify
from data import db_session, posts_api
from data.users import User
from data.posts import Post
from flask_login import LoginManager, login_user, logout_user, login_required
from forms.user import RegisterForm, LoginForm, EditForm
from forms.post import AddForm


app = Flask(__name__)
app.config['SECRET_KEY'] = 'NJwadok12LMKF3KMlmcd232v_key'
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


@app.route('/')
def base_site():
    db_sess = db_session.create_session()
    posts = db_sess.query(Post).all()
    return render_template('index.html', posts=posts[::-1], title='Twitterus')


@app.route('/user/<int:user_id>', methods=['GET', 'POST'])
def get_user(user_id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).get(user_id)
    if user:
        all_post = db_sess.query(Post).filter(Post.creater_id == user_id)
        return render_template('user.html', title=user.nick, name=user.name, about=user.about, posts=all_post, id=user_id)
    return jsonify({'error': 'user not found'})


@app.route('/edit/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).get(user_id)
    form = EditForm()
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
    if form.validate_on_submit():
        post = Post(
            title=form.title.data,
            creater_id=flask_login.current_user.id,
            text=form.text.data
        )
        db_sess = db_session.create_session()
        db_sess.add(post)
        db_sess.commit()
        return redirect('/')
    return render_template('add_post.html', title='Добавить пост', form=form)


def main():
    db_session.global_init("db/blogs.db")
    app.register_blueprint(posts_api.blueprint)
    app.run(port=8080, host='127.0.0.1')


if __name__ == '__main__':
    main()