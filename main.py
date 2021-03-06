import datetime
from flask import Flask, url_for, render_template, redirect, request, \
    make_response, session, abort, jsonify, g
from flask_login import LoginManager, current_user, login_user, login_manager, \
    login_required, logout_user

from forms.login import LoginForm
from forms.translate_form import TranslateForm
from forms.user import RegisterForm
from data import db_session, translate_api
from data.users import User
from data.history import History
from config import SECRET_KEY
from translation_core import ru_perevod_gl

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(
    days=365
)
login_manager = LoginManager()
login_manager.init_app(app)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.route('/register', methods=['GET', 'POST'])
def register():
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
        user = User(
            name=form.name.data,
            email=form.email.data,
            about=form.about.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route("/cookie_test")
def cookie_test():
    visits_count = int(request.cookies.get("visits_count", 0))
    if visits_count:
        res = make_response(
            f"Вы пришли на эту страницу {visits_count + 1} раз")
        res.set_cookie("visits_count", str(visits_count + 1),
                       max_age=60 * 60 * 24 * 365 * 2)
        return res
    res = make_response(
        "Вы пришли на эту страницу в первый раз за последние 2 года")
    res.set_cookie("visits_count", '1',
                   max_age=60 * 60 * 24 * 365 * 2)
    return res


@app.route("/session_test")
def session_test():
    visits_count = session.get('visits_count', 0)
    session['visits_count'] = visits_count + 1
    session['permanent'] = True
    return make_response(
        f"Вы пришли на эту страницу {visits_count + 1} раз")


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


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
def main_translate():
    form = TranslateForm()
    history_list = []

    if current_user.is_authenticated:
        db_sess = db_session.create_session()
        history_list = db_sess.query(History).filter(History.user_id ==
                                                     str(current_user.id)).all()[::-1]
        db_sess.close()

    if form.validate_on_submit():
        if not current_user.is_authenticated:
            return render_template('index.html', title="ⰒⰅⰓⰅⰂⰑⰄⰝⰋⰍⰠ ⰓⰀ ⰃⰎⰀⰃⰑⰎⰋⰜⰖ", form=form,
                                   result=ru_perevod_gl(form.content.data), history=[])
        db_sess = db_session.create_session()
        history = History()
        history.content = form.content.data
        history.result = ru_perevod_gl(form.content.data)
        current_user.history.append(history)
        db_sess.merge(current_user)
        db_sess.commit()
        history_list = db_sess.query(History).filter(History.user_id ==
                                                     str(current_user.id)).all()[::-1]
        db_sess.close()
        return render_template('index.html', title="ⰒⰅⰓⰅⰂⰑⰄⰝⰋⰍⰠ ⰓⰀ ⰃⰎⰀⰃⰑⰎⰋⰜⰖ", form=form,
                               result=ru_perevod_gl(form.content.data), history=history_list)
    return render_template('index.html', title='ⰒⰅⰓⰅⰂⰑⰄⰝⰋⰍⰠ ⰓⰀ ⰃⰎⰀⰃⰑⰎⰋⰜⰖ',
                           form=form, history=history_list)


@app.route('/old_trans_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def news_delete(id):
    db_sess = db_session.create_session()
    history_item = db_sess.query(History).filter(History.id == id,
                                                 History.user_id == str(current_user.id)
                                                 ).first()
    if history_item:
        db_sess.delete(history_item)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect('/')


def main():
    db_session.global_init("db/trans.sqlite3")
    app.register_blueprint(translate_api.blueprint)
    app.run()


if __name__ == '__main__':
    main()
