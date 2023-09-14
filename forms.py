from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import StringField, FloatField, FileField, SubmitField, validators


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[
        validators.InputRequired(),
        validators.Length(min=2, max=20),
        validators.Regexp('^[a-zA-Z]+$', message='Username must contain only letters')
    ])
    submit = SubmitField('Email login link')


class DeclarationForm(FlaskForm):
    meal_desc = StringField('Meal Description', validators=[validators.InputRequired(), validators.Length(min=4, max=40)])
    total_expenses = FloatField('Total expenses', validators=[validators.InputRequired(), validators.NumberRange(23.00, 123.00)])
    photo = FileField('Upload receipt', validators=[validators.InputRequired(), FileAllowed(['png'], 'PNG Images only!')])
    submit = SubmitField('Submit')
