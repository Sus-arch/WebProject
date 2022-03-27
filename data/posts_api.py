import flask
from flask import jsonify, request, redirect

from . import db_session
from .posts import Post


blueprint = flask.Blueprint(
    'posts_api',
    __name__,
    template_folder='templates'
)


@blueprint.route('/api/posts/del/<int:post_id>', methods=['GET', 'POST'])
def del_post(post_id):
    db_sess = db_session.create_session()
    post = db_sess.query(Post).get(post_id)
    db_sess.delete(post)
    db_sess.commit()
    return redirect(f'/user/{post.creater_id}')

