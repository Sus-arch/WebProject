from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, FileField
from wtforms.validators import DataRequired


class AddForm(FlaskForm):
    title = StringField('Заголовок', validators=[DataRequired()])
    text = TextAreaField('Текст поста')
    text_file = FileField('Приложите файл с текстом')
    submit = SubmitField('Добавить пост')


class EditPostForm(FlaskForm):
    title = StringField('Заголовок', validators=[DataRequired()])
    text = TextAreaField('Текст поста', validators=[DataRequired()])
    submit = SubmitField('Подтвердить изменения')