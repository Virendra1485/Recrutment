from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField, TextAreaField, SelectField, RadioField, DateField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, Regexp
from flask_login import current_user
from models import User, AdminUser


class AdminUserRegistrationForm(FlaskForm):
    full_name = StringField('Full Name',
                           validators=[DataRequired(), Length(min=2, max=20)])
    login_id = StringField('Login Id',
                        validators=[DataRequired(),
                                    Regexp(regex='^[a-z0-9A-Z]', message="Should start with alpha numeric characters")])

    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, full_name):
        adminuser = AdminUser.query.filter_by(full_name=full_name.data.strip()).first()
        if adminuser:
            raise ValidationError('This username is taken. Please choose a different one.')

    def validate_login_id(self, login_id):
        adminuser = AdminUser.query.filter_by(login_id=login_id.data.strip()).first()
        if adminuser:
            raise ValidationError('This login id taken. Please choose a different one.')


class RegistrationForm(FlaskForm):
    full_name = StringField('Full Name',
                           validators=[DataRequired(), Length(min=2, max=20)])
    login_id = StringField('Login Id',
                        validators=[DataRequired(),
                                    Regexp(regex='^[a-z0-9A-Z]', message="Should start with alpha numeric characters")])

    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')


    def validate_username(self, full_name):
        user = User.query.filter_by(full_name=full_name.data.strip()).first()
        if user:
            raise ValidationError('This username is taken. Please choose a different one.')

    def validate_login_id(self, login_id):
        user = User.query.filter_by(login_id=login_id.data.strip()).first()
        if user:
            raise ValidationError('This login id is taken. Please choose a different one.')


class LoginForm(FlaskForm):
    login_id = StringField('Login Id',
                        validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class RequestResetForm(FlaskForm):
    login_id = StringField('Login Id',
                        validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data.strip()).first()
        if user is None:
            raise ValidationError('There is no account with that login id. You must register first.')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')


class ApplicationForm(FlaskForm):
    name = StringField('name',
                           validators=[DataRequired(), Length(min=2, max=20)])
    sample_duration = IntegerField('Sample Duration',
                        validators=[DataRequired()])
    clean_air_duration = IntegerField('Clean Air Duration', validators=[DataRequired()])
    iteration = IntegerField('Iteration',
                                     validators=[DataRequired()])
    labels = TextAreaField('labels', validators=[DataRequired()])
    submit = SubmitField('Update')


class UploadForm(FlaskForm):
    name = StringField('Name')
    file_name = StringField('File Name')
    # date_created =
    no_of_record = IntegerField('No. Of Records')
    sample_date = StringField('Sample Date', validators=[DataRequired()])
    application_id = StringField('Application')
    label = StringField('Label')
    notes = TextAreaField('Notes')
    file = FileField('Upload Sample File', validators=[DataRequired(), FileAllowed(['csv', 'txt'])])
    support_file = FileField('Upload Supported Document')
    submit = SubmitField('Upload')


class RecordForm(FlaskForm):
    start_date = DateField('Start Date', format='%Y-%m-%d')
    end_time = DateField('End Date', format='%Y-%m-%d')
    submit = SubmitField('Submit')


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
    skill = StringField('Technical Proficiency')
    linked_link = StringField('Linkedin Link')
    skype_id = StringField('Skype Id')
    resume_remark = StringField('Resume Remark')
    resume = FileField('Resume', validators=[FileAllowed(['doc', 'docx', 'pdf'], 'only txt file allowed')])
    submit = SubmitField('Submit Form')

    def validate_email_id(self, email_id):
        user = User.query.filter_by(login_id=email_id.data.strip()).first()
        if user:
            raise ValidationError('Email Id is already taken. Try another')


class QuestionImport(FlaskForm):
    questions = FileField('', validators=[FileAllowed(['csv'], 'Only CSV File Allowed')])
    submit = SubmitField('upload')