from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField, SelectField, RadioField
from wtforms.validators import DataRequired, Length, Email, ValidationError
from models import User

class LoginForm(FlaskForm):
    login_id = StringField('Login Id',
                        validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class CandidateRegistrationForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(min=2, max=20)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=20)])
    email_id = StringField('Email', validators=[DataRequired(), Email()])
    mobile_no = StringField('Mobile No', validators=[DataRequired(), Length(min=10, max=10)])
    state = SelectField('State', choices=['Select', 'Madhya Pradesh', 'Uttar Pradesh', 'Maharastra'])
    city = StringField('City', validators=[DataRequired(), Length(min=2, max=20)])
    ssc_board = StringField('10th Board', validators=[DataRequired(), Length(min=2, max=20)])
    ssc_marks = IntegerField('SSC Marks', validators=[DataRequired()])
    hsc_board = StringField('12th Board', validators=[DataRequired(), Length(min=2, max=20)])
    hsc_marks = IntegerField('HSC Marks', validators=[DataRequired()])
    ug_degree = StringField('Degree Name', validators=[DataRequired(), Length(min=2, max=25)])
    ug_college = StringField('College', validators=[DataRequired(), Length(max=50)])
    ug_university = StringField('University Name', validators=[DataRequired(), Length(max=50)])
    ug_marks = IntegerField('Graduation Marks', validators=[DataRequired()])
    pg_degree = StringField('Post-Graduation')
    pg_college = StringField('College')
    pg_university = StringField('University Name')
    pg_marks = IntegerField('Post-Graduation Marks', default=0)
    skill = StringField('Technical Proficency')
    linked_link = StringField('Linkedin Link')
    skype_id = StringField('Skype Id')
    resume_remark = StringField('Resume Remark')
    resume = FileField('Resume', validators=[FileAllowed(['doc', 'docx', 'pdf'], 'Only Pdf, Doc and Docx File Allowed')])
    submit = SubmitField('Submit Form')

    def validate_email_id(self, email_id):
        user = User.query.filter_by(login_id=email_id.data.strip()).first()
        if user:
            raise ValidationError('Email Id is already taken. Try another')

class TestForm(FlaskForm):
    options = RadioField()
    
    
