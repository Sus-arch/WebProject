from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, TextAreaField, SubmitField, EmailField, BooleanField
from wtforms.validators import DataRequired


class AddForm(FlaskForm):
    title = StringField('Заголовок', validators=[DataRequired()])
    text = TextAreaField('Текст поста', validators=[DataRequired()])
    submit = SubmitField('Добавить пост')


class EditPostForm(FlaskForm):
    title = StringField('Заголовок', validators=[DataRequired()])
    text = TextAreaField('Текст поста', validators=[DataRequired()])
    submit = SubmitField('Подтвердить изменения')