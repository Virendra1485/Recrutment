import logging
import os
import csv
import io

import zmq
from time import sleep
from datetime import datetime

from flask_mail import Message, Mail
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, send_from_directory, session
from flask_login import login_user, current_user, logout_user, login_required
from werkzeug import secure_filename

from models import User, AdminUser, Candidate, Question, QuestionSet, UserQuestionSet
from api_server import db, bcrypt, mail, login_manager
from config import Config

from .forms import AdminUserRegistrationForm, RegistrationForm, LoginForm, RequestResetForm, \
    ResetPasswordForm, RecordForm, CandidateRegistrationForm, QuestionImport

from sqlalchemy import create_engine


admin = Blueprint('admin', __name__, url_prefix="/admin")



context = zmq.Context.instance()
publisher = context.socket(zmq.PUB)
zmq_uri = Config.USER_UPDATE_NOTIFICATION_EP
publisher.bind(zmq_uri)
sleep(1)


def publish_zmq_message(email, action="UPDATE_USER"):
    data = [action, str(email)]
    logging.info(f"publish_zmq_message,data: {data}")
    new_data = [x.encode('utf-8') for x in data]
    logging.info(f"publish_zmq_message: {new_data}")
    publisher.send_multipart(new_data)
    logging.info(f"Message published {str(datetime.now())}")


@admin.route('/user_list', methods=['GET', 'POST'])
def userlist():
    users = User.query.all()
    return render_template('users_list.html', title='User List', users=users)


@admin.route("/<secret_key>/register/", methods=['POST', 'GET'])
def register(secret_key):
    if secret_key == Config.SECRET_KEY:
        if current_user.is_authenticated:
            return redirect(url_for('admin.login'))
        form = AdminUserRegistrationForm()

        if form.validate_on_submit():
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            user = AdminUser(full_name=form.full_name.data.strip(), login_id=form.login_id.data.strip(), password=hashed_password)
            db.session.add(user)
            db.session.commit()
            flash('Your account has been created! You are now able to log in', 'success')
            logging.info(f"register, Admin registered successfully Login Id: {form.login_id.data.strip()}")
            return redirect(url_for('admin.login'))
        return render_template('register.html', title='Register', form=form)
    else:
        return "Page Not Found"


@admin.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin.login'))

    form = LoginForm()
    if form.validate_on_submit():
        user = AdminUser.query.filter_by(login_id=form.login_id.data.strip()).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data.strip()):
            login_user(user, remember=form.remember.data,force=True)
            next_page = request.args.get('next')
            logging.info(f"login, Admin logged in successfully Login Id: {form.login_id.data.strip()}")
            return redirect(url_for('admin.dashboard'))
        else:
            flash('Login Unsuccessful. Please check login_id and password', 'danger')
            logging.info(f"login, Admin log in unsuccessful Login Id: {form.login_id.data.strip()}")

    return render_template('login.html', title='Login', form=form)


@admin.route("/logout")
def logout():
    logout_user()
    logging.info(f"logout, Admin logged out successfully")
    return redirect(url_for('admin.login'))


@admin.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(login_id=form.login_id.data.strip()).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('admin.login'))
    return render_template('reset_request.html', title='Reset Password', form=form)


@admin.route('/add_user', methods = ['POST','GET'])
@login_required
def add_user():
    if not current_user.is_authenticated:
        return redirect(url_for('admin.login'))

    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data.strip()).decode('utf-8')
        entry = User(full_name=form.full_name.data.strip(), login_id=form.login_id.data.strip(), password=hashed_password)
        db.session.add(entry)
        db.session.commit()
        flash('new user has been created! ', 'success')
        logging.info(f"add_user, New User created Login Id: {form.login_id.data.strip()}")
        return redirect(url_for('admin.userlist'))
    return render_template('add_user.html', title='Register', form=form)


@admin.route("/edit_password/<int:id>", methods=['GET', 'POST'])
@login_required
def edit_password(id):
    if not current_user.is_authenticated:
        return redirect(url_for('admin.login'))

    form = RegistrationForm()
    user = User.query.get(id)
    user.enable = True
    if request.method == 'POST':
        userdb = User.query.filter_by(id=id, enable=True).first()
        db_password = userdb.password
        if form.password.data.strip() == form.confirm_password.data.strip():
            if userdb and bcrypt.check_password_hash(db_password, form.password.data):
                flash("Previous password can not be use", "danger")
                logging.info(f"edit_password, User password reset failed due to same old password Login Id: {user.login_id}")
                return render_template('edit_password.html', form=form, name=user.full_name, login_id=user.login_id)

        if form.password.data.strip() == form.confirm_password.data.strip():
            hashed_password = bcrypt.generate_password_hash(form.password.data.strip()).decode('utf-8')
            user.password = hashed_password
            user.enable = True
            db.session.commit()
            flash("Password has been reset .", "success")
            logging.info(f"edit_password, User password updated Login Id: {user.login_id}")

            publish_zmq_message(user.login_id)
            return redirect(url_for('admin.userlist'))
        else:
            flash("Password does not match.", "danger")
            logging.info(f"edit_password, User password update failed Login Id: {user.login_id}")
    return render_template('edit_password.html',form=form,name=user.full_name, login_id=user.login_id)


@admin.route("/delete_user/<int:id>")
@login_required
def delete_user(id):
    if not current_user.is_authenticated:
        return redirect(url_for('admin.login'))

    entry = User.query.get(id)
    db.session.delete(entry)
    db.session.commit()
    publish_zmq_message(entry.login_id)
    flash("User has been deleted .", "success")
    logging.info(f"delete_user, User deleted Id: {id}, Login Id: {entry.login_id}")
    return redirect(url_for('admin.userlist'))


@admin.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('admin.userlist'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('This is an invalid or expired landing token', 'warning')
        return redirect(url_for('users.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data.strip()).decode('utf-8')
        user.password = hashed_password
        user.enable = True
        db.session.commit()
        publish_zmq_message(user.login_id)
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('admin.landing'))
    return render_template('reset_token.html', title='Reset Password', form=form)


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('password reset request', sender='mukherjidev1@gmail.com', recipients=[user.email])

    msg.body = f'''to reset your password visit link { url_for('admin.reset_token', token=token, _external=True)}'''
    logging.info(f"reset password: {msg}")
    mail.send(msg)


@admin.route('/landing')
def landing():
    return render_template('landing.html')

@login_required
@admin.route('/userlist_u/<user_id>', methods=['GET', 'POST'])
def userlist_u(user_id):
    if not current_user.is_authenticated:
        return redirect(url_for('admin.login'))

    user = User.query.filter_by(id=user_id).first()
    if user.enable:
        user.enable = False
    else:
        user.enable = True
    db.session.commit()

    if user.enable:
        flash("User has been set to Active ", 'success')
        logging.info(f"userlist_u, User enabled Login Id: {user.login_id}")
    else:
        flash("User has been set to InActive ", 'success')
        logging.info(f"userlist_u, User disabled Login Id: {user.login_id}")
    publish_zmq_message(user.login_id)
    return redirect(url_for('admin.userlist'))


@login_required
@admin.route('/assign_test/<login_id>', methods=['GET', 'POST'])
def assign_test(login_id):
    user = UserQuestionSet.query.filter_by(login_id=login_id).first()
    user_name = User.query.filter_by(login_id=login_id).first()
    return render_template('assign_test.html', user=user, user_name=user_name, status=Config.STATUS, result_status=Config.RESULT_STATUS)


@login_required
@admin.route('/add_test/<login_id>', methods=['GET', 'POST'])
def add_test(login_id):
    entry = UserQuestionSet(login_id=login_id, status=0)
    user = UserQuestionSet.query.filter_by(login_id=login_id).first()
    if not user:
        db.session.add(entry)
        db.session.commit()
    user = UserQuestionSet.query.filter_by(login_id=login_id).first()

    check_user = QuestionSet.query.filter_by(user_question_set_id=user.id).first()
    if check_user:
        flash("Test Already Assign To The User", 'success')
    else:
        test_question(user.id)
        flash("Test Assign To The User ", 'success')
    return redirect(url_for('admin.assign_test', login_id=login_id))


@login_required
@admin.route('/delete_test/<login_id>', methods=['GET', 'POST'])
def delete_test(login_id):
    entry = UserQuestionSet.query.filter_by(login_id=login_id).first()
    entry1 = QuestionSet.query.filter_by(user_question_set_id=entry.id).first()
    db.session.delete(entry)
    db.session.delete(entry1)
    db.session.commit()
    return redirect(url_for('admin.assign_test', login_id=login_id))

@login_required
@admin.route('/dashboard')
def dashboard():

    return render_template('dashboard.html', title="Admin Dashboard")

@login_required
@admin.route('/report', methods=['GET', 'POST'])
def report():
    if current_user.is_authenticated:
        return redirect(url_for('admin.login'))

    form = RecordForm()
    if form.validate_on_submit():
        start_date = str(form.start_date.data) + " " + "00:00:00"
        end_date = str(form.end_time.data) + " " + "23:59:59"
        engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
        with engine.connect() as conn:
            query_string = f"select DATE_FORMAT(start_time, '%%Y-%%m-%%d %%h:%%i:%%s') as start_time, DATE_FORMAT(end_time, '%%Y-%%m-%%d %%h:%%i:%%s') as end_time," \
                           f"DATE_FORMAT(date_modified, '%%Y-%%m-%%d') as date_modified, login_id, status, marks, result_status from user_question_set_tbl " \
                           f"where date_modified between '{start_date}' and '{end_date}';"
            records = conn.execute(query_string)
        return render_template('report_tbl.html', title="User Records", records=records, status=Config.STATUS,
                               result_status=Config.RESULT_STATUS)
    return render_template('report.html', title="User Records", form=form)


def test_question(id):
    count = 1
    for x in range(1, Config.TEST_DIFFICULTY_LEVEL+1):
        engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
        with engine.connect() as conn:
            query_string = f"SELECT r1.id as id, answer FROM questions AS r1 JOIN (SELECT CEIL(RAND() * (SELECT MAX(id)-10 FROM questions " \
                           f"where difficulty_level = {x})) AS id) AS r2 WHERE r1.id >= r2.id and difficulty_level = {x}  " \
                           f"ORDER BY r1.id ASC  LIMIT {Config.NO_OF_QUESTION_EACH_LEVEL};"
            records = conn.execute(query_string)
            for record in records:
                entry = QuestionSet(user_question_set_id=id, question_id=record.id, answer=record.answer,
                                    chosen_answer="", sequence_no=count, status=0,
                                    is_last=True if count == Config.TEST_DIFFICULTY_LEVEL * Config.NO_OF_QUESTION_EACH_LEVEL else False)
                db.session.add(entry)
                db.session.commit()
                count = count+1

def result():
    engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
    with engine.connect() as conn:
        query_string = "select count(chosen_answer) from question_set where chosen_answer in (select answer from questions);"
        records = conn.execute(query_string)
        for record in records:
            marks = record[0]
    return marks


@login_required
@admin.route('/add_candidate', methods=['GET', 'POST'])
def add_candidate():
    form = CandidateRegistrationForm()
    if form.validate_on_submit():
        uploaded_file = request.files['resume']
        resume_dir = './uploaded_resume'

        if not os.path.exists(resume_dir):
            os.makedirs(resume_dir)

        date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = date_str + "_" + uploaded_file.filename
        uploaded_file.save(os.path.join(resume_dir, secure_filename(file_name)))
        hashed_password = bcrypt.generate_password_hash(Config.DEFAULT_PASSWORD).decode('utf-8')
        entry = Candidate(first_name=form.first_name.data, last_name=form.last_name.data, email_id=form.email_id.data,
                          password=hashed_password, mobile_no=form.mobile_no.data, state=form.state.data, city=form.city.data,
                          ssc_board=form.ssc_board.data, ssc_marks=form.ssc_marks.data, hsc_board=form.hsc_board.data,
                          hsc_marks=form.hsc_marks.data, ug_degree=form.ug_degree.data, ug_college=form.ug_college.data,
                          ug_university=form.ug_university.data, ug_marks=form.ug_marks.data, pg_degree=form.pg_degree.data,
                          pg_college=form.pg_college.data, pg_university=form.pg_university.data, pg_marks=form.pg_marks.data,
                          skill=form.skill.data, linked_link=form.linked_link.data, skype_id=form.skype_id.data,
                          resume_remark=form.resume_remark.data, resume=file_name, registered_by=1)
        full_name = form.first_name.data + " " + form.last_name.data
        user_entry = User(full_name=full_name, login_id=form.email_id.data, password=hashed_password)
        db.session.add(user_entry)
        db.session.add(entry)
        db.session.commit()
        flash('Your account has been created!', 'success')
        return redirect(url_for('admin.userlist'))
    return render_template('candidate_registration.html', title="User Records", form=form)


@login_required
@admin.route('/update_candidate/<login_id>', methods=['GET', 'POST'])
def update_candidate(login_id):
    candidate = Candidate.query.filter_by(email_id=login_id).first()
    form = CandidateRegistrationForm(obj=candidate)
    if form.validate_on_submit():

        user = User.query.filter_by(login_id=login_id).first()
        user.full_name = form.first_name.data + " " + form.last_name.data

        uploaded_file = request.files['resume']
        resume_dir = './uploaded_resume'

        if not os.path.exists(resume_dir):
            os.makedirs(resume_dir)

        date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = date_str + "_" + uploaded_file.filename
        uploaded_file.save(os.path.join(resume_dir, secure_filename(file_name)))

        candidate.first_name = form.first_name.data
        candidate.last_name = form.last_name.data
        candidate.mobile_no = form.mobile_no.data
        candidate.state = form.state.data
        candidate.city = form.city.data
        candidate.ssc_board = form.ssc_board.data
        candidate.ssc_marks = form.ssc_marks.data
        candidate.hsc_board = form.hsc_board.data
        candidate.hsc_marks = form.hsc_marks.data
        candidate.ug_degree = form.ug_degree.data
        candidate.ug_college = form.ug_college.data
        candidate.ug_university = form.ug_university.data
        candidate.ug_marks = form.ug_marks.data
        candidate.pg_degree = form.pg_degree.data
        candidate.pg_college = form.pg_college.data
        candidate.pg_university = form.pg_university.data
        candidate.pg_marks = form.pg_marks.data
        candidate.skill = form.skill.data
        candidate.linked_link = form.linked_link.data
        candidate.skype_id = form.skype_id.data
        candidate.resume_remark = form.resume_remark.data
        candidate.resume = file_name
        candidate.registered_by = 1

        db.session.commit()
        flash('Your account has been Updated!', 'success')
        return redirect(url_for('admin.userlist'))
    return render_template('update_candidate.html', title="User Records", form=form, user=login_id)


@login_required
@admin.route('/question_import', methods=['GET', 'POST'])
def question_import():
    form = QuestionImport()
    if form.validate_on_submit():
        file = request.files['questions']
        print(file.filename)
        # file_contents = file.stream.read().decode("utf-8")
        # csv_input = csv.reader(file_contents)
        # for row in csv_input:
        #     print(row)

        with open(file.filename, 'r') as csv_file:
            csv_reader = csv.reader(csv_file)
            for x in csv_reader:
                print(x)

    return render_template('question_import.html', title="Import Question", form=form)

@login_required
@admin.route('/import_csv', methods=['GET', 'POST'])
def import_csv():
    form = QuestionImport()
    if form.validate_on_submit():
        file = request.files['questions']
        print(file.filename) 
        stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
        reader = csv.DictReader(stream, delimiter=';')
        for row in reader:
            entry = Question(question=row.get('question'), code=row.get('code'), optionA=row.get('optionA'), optionB=row.get('optionB'),
                           optionC=row.get('optionC'), optionD=row.get('optionD'), answer=row.get('answer'),
                           difficulty_level=row.get('difficulty_level'), type=row.get('type'))
            db.session.add(entry)
            db.session.commit()
    return render_template('question_import.html', title="Import Question", form=form)