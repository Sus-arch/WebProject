import flask
from flask import jsonify, request, redirect

from . import db_session
from .posts import Post


blueprint = flask.Blueprint(
    'posts_api',
    __name__,
    template_folder='templates'
)


@blueprint.route('/api/posts/del/<int:post_id>/<int:user_id>', methods=['GET', 'POST'])
def del_post(post_id, user_id):
    db_sess = db_session.create_session()
    all_post = db_sess.query(Post).filter(Post.creater_id == user_id)
    i = 0
    for post in all_post:
        if post_id - 1 == i:
            db_sess.delete(post)
        i += 1
    db_sess.commit()
    return redirect(f'/user/{user_id}')
