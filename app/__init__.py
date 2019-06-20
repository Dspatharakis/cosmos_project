from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from celery import Celery
import celeryconfig
from flask_migrate import Migrate

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
from app import routes, models

def make_celery(app):
    # create context tasks in celery
    celery = Celery(
        app.import_name,
        broker=app.config['BROKER_URL']
    )
    celery.conf.update(app.config)
    celery.config_from_object(celeryconfig)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask

    return celery

celery = make_celery(app)
