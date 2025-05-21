from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length

class PostForm(FlaskForm):
    title = StringField('Titolo', validators=[DataRequired(), Length(min=1, max=140)])
    content = TextAreaField('Contenuto', validators=[DataRequired()])
    submit = SubmitField('Pubblica')