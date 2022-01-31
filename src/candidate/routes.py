import logging
import os

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

from .forms import LoginForm, CandidateRegistrationForm, TestForm

from sqlalchemy import create_engine

candidate = Blueprint('candidate', __name__)

@candidate.route('/candidate_registration', methods=['GET', 'POST'])
def candidate_registration():
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
                          resume_remark=form.resume_remark.data, resume=file_name, registered_by=2)
        full_name = form.first_name.data + " " + form.last_name.data
        user_entry = User(full_name=full_name, login_id=form.email_id.data, password=hashed_password)
        db.session.add(user_entry)
        db.session.add(entry)
        db.session.commit()
        flash('Your account has been created!', 'success')
        return redirect(url_for('candidate.candidate_login'))

    return render_template('candidate_registration.html', form=form)

@login_required
@candidate.route('/login', methods=['GET', 'POST'])
def candidate_login():
    if current_user.is_authenticated:
        return redirect(url_for('candidate.start_test'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(login_id=form.login_id.data.strip(), enable=True).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data.strip()):
            login_user(user, remember=form.remember.data, force=True)
            session['login_id'] = form.login_id.data.strip()
            return redirect(url_for('candidate.start_test'))
        else:
            flash('Login Unsuccessful. Please check login_id and password', 'danger')
            logging.info(f"login, Admin log in unsuccessful Login Id: {form.login_id.data.strip()}")

    return render_template('candidate_login.html', title='Login', form=form)

@login_required
@candidate.route('/start_test')
def start_test():
    if not current_user.is_authenticated:
        return redirect(url_for('candidate.candidate_login'))

    user = UserQuestionSet.query.filter_by(login_id=session['login_id']).first()
    if not user:
        return render_template('start_test.html', title='Start Assessment', user=user)
    if not user.status == 3:
        user.date_modified = datetime.now()
        user.status = 1
        user.start_time = datetime.now()
        db.session.commit()
    return render_template('start_test.html', title='Start Assessment', user=user)


@login_required
@candidate.route('/test/<sequence_no>', methods=['GET', 'POST'])
@candidate.route('/test', methods=['GET', 'POST'])
def test(sequence_no=None):
    if not current_user.is_authenticated:
        return redirect(url_for('candidate.candidate_login'))

    if not sequence_no:
        sequence_no = 1
    sequence_no = int(sequence_no)

    user_question_set = UserQuestionSet.query.filter_by(login_id=session["login_id"]).first()
    if not user_question_set:
        flash('Sorry You Have No Assigned Test', 'success')
        return redirect(url_for('candidate.start_test'))

    questions_set = QuestionSet.query.filter_by(sequence_no=sequence_no, user_question_set_id=user_question_set.id).first()

    if not questions_set and sequence_no == 1:
        flash('Sorry You Have No Assigned Test', 'success')
        return redirect(url_for('candidate.start_test'))

    if not questions_set:
        return redirect(url_for('candidate.candidate_result'))

    question = Question.query.filter_by(id=questions_set.question_id).first()
    form = TestForm()
    form.options.choices = [('A', question.optionA), ('B', question.optionB), ('C', question.optionC), ('D', question.optionD)]
    if request.method == "GET":
        if questions_set.status == 1 and questions_set.chosen_answer:
            form.options.data = questions_set.chosen_answer

    if form.validate_on_submit():
        questions_set.chosen_answer = form.options.data
        db.session.commit()
        if questions_set.is_last:
            questions_set.status = 2
            user_question_set.status = 2
            db.session.commit()
            return redirect(url_for('candidate.candidate_result', sequence_no=sequence_no+1))
        else:
            questions_set.status = 1
            db.session.commit()
            return redirect(url_for('candidate.test', sequence_no=sequence_no + 1))
    return render_template('test.html', title='Candidate Test', form=form, question=question, questions_set=questions_set,
                           sequence_no=sequence_no)


@candidate.route('/candidate_result')
@login_required
def candidate_result():
    if not current_user.is_authenticated:
        return redirect(url_for('candidate.candidate_login'))
    login_id = session['login_id']
    marks = result()
    record = UserQuestionSet.query.filter_by(login_id=login_id).first()
    record.end_time = datetime.now()
    record.marks = marks
    record.status = 3
    record.result_status = 1
    db.session.commit()
    return render_template('candidate_result.html', title='Candidate Result', marks=marks, login_id=login_id)


@candidate.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('candidate.candidate_login'))


def result():
    engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
    with engine.connect() as conn:
        query_string = "select count(chosen_answer) from question_set where chosen_answer in (select answer from questions);"
        records = conn.execute(query_string)
        for record in records:
            marks = record[0]
    return marks


# @login_manager.unauthorized_handler     # In unauthorized_handler we have a callback URL
# def unauthorized_callback():            # In call back url we can specify where we want to
#        return redirect(url_for('login')) # redirect the user in my case it is login page!
