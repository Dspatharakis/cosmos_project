import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    # ...
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    REDIS_HOST = "0.0.0.0"
    REDIS_PORT = 6379
    BROKER_URL = 'redis://localhost:6379'
    CELERY_RESULT_BACKEND = BROKER_URL