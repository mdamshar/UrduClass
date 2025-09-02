from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, RadioField, TextAreaField
from wtforms.validators import DataRequired, EqualTo, Length, ValidationError
from models import User

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(), 
        Length(min=4, max=20, message='Username must be between 4 and 20 characters')
    ])
    password = PasswordField('Password', validators=[
        DataRequired(), 
        Length(min=6, message='Password must be at least 6 characters')
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(), 
        EqualTo('password', message='Passwords must match')
    ])
    
    full_name = StringField("Full Name", validators=[DataRequired()])
    fathers_name = StringField("Father's Name", validators=[DataRequired()])
    address = StringField("Address", validators=[DataRequired()])
    student_class = StringField("Class", validators=[DataRequired()])
    contact_number = StringField("Contact Number", validators=[DataRequired(), Length(10, 20)])
    
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already exists. Choose a different one.')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class QuestionForm(FlaskForm):
    text = TextAreaField('Question Text', validators=[
        DataRequired(), 
        Length(min=10, message='Question must be at least 10 characters')
    ])
    option_a = StringField('Option A', validators=[DataRequired()])
    option_b = StringField('Option B', validators=[DataRequired()])
    option_c = StringField('Option C', validators=[DataRequired()])
    option_d = StringField('Option D', validators=[DataRequired()])
    correct_answer = RadioField('Correct Answer', 
        choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')], 
        validators=[DataRequired()]
    )
    submit = SubmitField('Save Question')

class AssessmentForm(FlaskForm):
    submit = SubmitField('Submit Assessment')