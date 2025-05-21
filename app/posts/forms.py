from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length, Optional

class PostForm(FlaskForm):
    title = StringField('Titolo', validators=[DataRequired(), Length(min=1, max=140)])
    content = TextAreaField('Contenuto', validators=[DataRequired()])
    image_file = FileField('Allega immagine', validators=[
        FileAllowed(['jpg', 'png', 'jpeg'], 'Solo immagini JPG/PNG!'),
        Optional()
    ])
    image_url = StringField('URL immagine esterna', validators=[Optional()])
    submit = SubmitField('Pubblica')