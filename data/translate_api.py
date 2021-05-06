import flask
from flask import jsonify, request

from . import db_session
from .history import History
from .users import User
from translation_core import ru_perevod_gl

blueprint = flask.Blueprint(
    'translate_api',
    __name__,
    template_folder='templates'
)


@blueprint.route('/api/translate/')  # /api/translate/words&optional_example@mail.com
@blueprint.route('/api/show_history/')  # /api/show_history/example@mail.com&password
def api_empty():
    return jsonify({'error': 'Not found arguments of request'})


@blueprint.route('/api/translate/<content>')  # /api/translate/words&optional_example@mail.com
def api_get_result(content):
    delimiter = content.rfind('&')
    db_sess = db_session.create_session()

    if delimiter != -1:
        result = ru_perevod_gl(content[:delimiter])
        user = db_sess.query(User).filter(User.email == content[delimiter + 1:]).first()
        if user:
            history = History(
                content=content[:delimiter],
                result=result,
                user_id=user.id
            )
            db_sess.add(history)
            db_sess.commit()
            return jsonify({
                'user': user.name,
                'result': result
            })

        return jsonify({'error': 'User not found'})

    db_sess.close()

    return jsonify({
        'result': ru_perevod_gl(content)
    })


@blueprint.route('/api/show_history/<client>')  # /api/show_history/example@mail.com&password
def api_show_history(client):
    db_sess = db_session.create_session()

    delimiter = client.rfind('&')
    if delimiter == -1:
        return jsonify({'error': 'Syntax error'})

    user = db_sess.query(User).filter(User.email == client[:delimiter]).first()
    if not user:
        return jsonify({'error': 'User not found'})

    if not user.check_password(client[delimiter + 1:]):
        return jsonify({'error': 'Wrong password'})

    history = db_sess.query(History).filter(History.user_id == user.id).all()
    db_sess.close()
    return jsonify([item.to_dict(only=('content', 'result', 'created_date'))
                    for item in history])


@blueprint.route('/api/about/')
def api_about():
    return jsonify({
        'name': 'ⰒⰅⰓⰅⰂⰑⰄⰝⰋⰍⰠ ⰓⰀ ⰃⰎⰀⰃⰑⰎⰋⰜⰖ - Переводчик с русского языка на глаголицу',
        'official site': 'https://github.com/SUPERustam/Translater',
        'source code': 'https://github.com/SUPERustam/Translater',
        'api requests and examples':
            [{'get translation': '/api/translate/words&optional_example@mail.com',
              'show history': 'api/show_history/example@mail.com&password'}],
        'message': 'Please, star our project: https://github.com/SUPERustam/Translater'
                   ' and share this site with others :heart:'
    })
