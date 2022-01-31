from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from api_server import db, ma, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return AdminUser.query.get(int(user_id))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class BaseModel():
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    date_modified = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


class User(BaseModel, db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    full_name = db.Column(db.String(256), nullable=False)
    login_id = db.Column(db.String(256), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=True)
    enable = db.Column(db.Boolean, nullable=False, default=False)

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(current_app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"User('{self.full_name}', '{self.login_id}')"


class AdminUser(BaseModel, db.Model, UserMixin):
    __tablename__ = 'admin_user'
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(256), nullable=False)
    login_id = db.Column(db.String(256), nullable=False, unique=True)
    password = db.Column(db.String(256), nullable=False)

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(current_app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return

    def __repr__(self):
        return f"AdminUser('{self.full_name}', '{self.login_id}', '{self.login_id}')"


class Candidate(BaseModel, db.Model, UserMixin):
    __tablename__ = 'candidate'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String(256), nullable=False)
    last_name = db.Column(db.String(256), nullable=False)
    email_id = db.Column(db.String(256), nullable=False)
    password = db.Column(db.String(256), nullable=False)
    mobile_no = db.Column(db.String(10), nullable=False)
    state = db.Column(db.String(256), nullable=False)
    city = db.Column(db.String(256), nullable=False)
    ssc_board = db.Column(db.String(256), nullable=False)
    ssc_marks = db.Column(db.Integer)
    hsc_board = db.Column(db.String(256), nullable=False)
    hsc_marks = db.Column(db.Integer)
    ug_degree = db.Column(db.String(256), nullable=False)
    ug_college = db.Column(db.String(256), nullable=False)
    ug_university = db.Column(db.String(256), nullable=False)
    ug_marks = db.Column(db.Integer, default=0)
    pg_degree = db.Column(db.String(256))
    pg_college = db.Column(db.String(256))
    pg_university = db.Column(db.String(256))
    pg_marks = db.Column(db.Integer, default=0)
    skill = db.Column(db.String(256))
    linked_link = db.Column(db.String(256))
    skype_id = db.Column(db.String(256))
    resume_remark = db.Column(db.String(256))
    resume = db.Column(db.String(256), nullable=False)
    registered_by = db.Column(db.Integer)

    def __repr__(self):
        return f"CandidateUser('{self.first_name}', '{self.email_id}')"


class Question(db.Model, UserMixin):
    __tablename__ = 'questions'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    question = db.Column(db.String(256), nullable=False)
    code = db.Column(db.String(256), nullable=False)
    optionA = db.Column(db.String(256), nullable=False)
    optionB = db.Column(db.String(256), nullable=False)
    optionC = db.Column(db.String(256), nullable=False)
    optionD = db.Column(db.String(256), nullable=False)
    answer = db.Column(db.String(256), nullable=False)
    difficulty_level = db.Column(db.Integer, nullable=False)
    type = db.Column(db.String(256), nullable=False)


class UserQuestionSet(BaseModel, db.Model, UserMixin):
    __tablename__ = 'user_question_set_tbl'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    login_id = db.Column(db.String(256), nullable=False)
    status = db.Column(db.Integer, nullable=False)
    start_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    end_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    marks = db.Column(db.Integer, nullable=False, default=0)
    result_status = db.Column(db.Integer, nullable=False, default=0)


class QuestionSet(db.Model, UserMixin):
    __tablename__ = 'question_set'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_question_set_id = db.Column(db.Integer, db.ForeignKey(UserQuestionSet.__tablename__ + '.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey(Question.__tablename__ + '.id'), nullable=False)
    answer = db.Column(db.String(256), nullable=False)
    chosen_answer = db.Column(db.String(256), nullable=False)
    sequence_no = db.Column(db.Integer, nullable=False)
    status = db.Column(db.Integer, nullable=False)
    is_last = db.Column(db.Boolean, nullable=False, default=False)






