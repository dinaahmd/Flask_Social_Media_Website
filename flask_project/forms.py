from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask_project.models import User

# Classes that repreasent our forms in python
class RegistrationForm(FlaskForm):
    # Allow Username from 2 chars to 20 chars
    username = StringField(
        'Username',
        validators=[
            DataRequired(),
            Length(min=2, max=20)
        ]
    )
    email = StringField(
        'Email',
        validators=[
            DataRequired(),
            Email()
        ]
    )
    password = PasswordField(
        'Password',
        validators=[
            DataRequired()
        ]
    )
    confirm_password = PasswordField(
        'Confirm Password',
        validators=[
            DataRequired(),
            EqualTo('password')
        ]
    )
    submit = SubmitField(
        'Sign Up'
    )

    # Custom Validation Functions for duplicats
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError("Username is taken, please choose another Username")

    def validate_email(self, email):
        email = User.query.filter_by(email=email.data).first()
        if email:
            raise ValidationError("Email is taken, please choose another Email")

class LoginForm(FlaskForm):
    username = StringField(
        'Username',
        validators=[
            DataRequired(),
            Length(min=2, max=20)
        ]
    )
    password = PasswordField(
        'Password',
        validators=[
            DataRequired()
        ]
    )
    submit = SubmitField(
        'Login'
    )

class PostForm(FlaskForm):
    content = StringField(
    'Content', 
    validators=[
        DataRequired()]
    )
    privacy = SelectField(
    'Privacy', 
    choices=[('public', 'Public'), ('friends', 'Friends Only'), ('private', 'Only Me')]
    )
    submit = SubmitField(
        'Post'
    )
    
   