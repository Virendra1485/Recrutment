import os
import logging
from datetime import timedelta
from flask_mail import Mail

class Config:
    LOG_LEVEL = os.environ.get('LOG_LEVEL', '')
    if LOG_LEVEL == '1':
        log_level = logging.DEBUG
    elif LOG_LEVEL == '2':
        log_level = logging.INFO
    elif LOG_LEVEL == '4':
        log_level = logging.ERROR
    elif LOG_LEVEL == '5':
        log_level = logging.CRITICAL
    else:
        log_level = logging.WARNING

    SECRET_KEY = '605c647fe18922474e9ed146ca05bfcb'

    PORT = int(os.environ.get('PORT'))
    print('PORT : ', PORT)
    THREAD_COUNT = int(os.environ.get('THREAD_COUNT', 2))
    print('THREAD_COUNT : ', THREAD_COUNT)

    SQLALCHEMY_DATABASE_URI = os.environ.get('DB_URL')
    print('DB_URL  : ', SQLALCHEMY_DATABASE_URI)
    if not SQLALCHEMY_DATABASE_URI:
        print("DB_URL not set . Quiting")
        exit(1)

    USER_UPDATE_NOTIFICATION_EP = os.environ.get('USER_UPDATE_NOTIFICATION_EP')
    print('USER_UPDATE_NOTIFICATION_EP  : ', USER_UPDATE_NOTIFICATION_EP)
    if not USER_UPDATE_NOTIFICATION_EP:
        print("USER_UPDATE_NOTIFICATION_EP not set . Quiting")
        exit(1)


    JWT_SECRET_KEY = "daf660012e0e167147acc8a2342e75f"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)

    LOGIN_URL = os.environ.get('LOGIN_URL')
    if not LOGIN_URL:
        print("LOGIN_URL not set . Quiting")
        exit(1)

    DEFAULT_PASSWORD = os.environ.get('DEFAULT_PASSWORD')
    if not DEFAULT_PASSWORD:
        print("DEFAULT_PASSWORD not set . Quiting")
        exit(1)

    TEST_DIFFICULTY_LEVEL = int(os.environ.get('TEST_DIFFICULTY_LEVEL', 2))
    if not TEST_DIFFICULTY_LEVEL:
        print("TEST_DIFFICULTY_LEVEL not set . Quiting")
        exit(1)

    NO_OF_QUESTION_EACH_LEVEL = int(os.environ.get('NO_OF_QUESTION_EACH_LEVEL', 10))
    if not NO_OF_QUESTION_EACH_LEVEL:
        print("NO_OF_QUESTION_EACH_LEVEL not set . Quiting")
        exit(1)

    SUCCESS_PERCENTAGE = os.environ.get('SUCCESS_PERCENTAGE')
    if not SUCCESS_PERCENTAGE:
        print("SUCCESS_PERCENTAGE not set . Quiting")
        exit(1)

    PROPAGATE_EXCEPTIONS = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    RESTPLUS_MASK_SWAGGER = False
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'deepakkanthi2006@gmail.com'
    MAIL_PASSWORD = 'Admin@123'


    ERROR_CODE = {
        0: 'Success',
        1: 'user Exist with email ',
        2: 'User Not Exist',
        4: 'Password Not Matched',
        5: 'Invalid action',
        500: 'General Exception',
        100: 'Database Exception'
    }

    STATUS = {
        0: 'Initial Value',
        1: 'Test Started',
        2: 'Test Completed',
        3: 'Result Generate'
    }

    RESULT_STATUS = {
        0: 'Fail',
        1: 'Pass'
    }