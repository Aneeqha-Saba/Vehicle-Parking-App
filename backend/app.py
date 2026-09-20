from flask import Flask
from application.config import LocalDevelopmentConfig
from application.database import db
from application.models import User
from application.security import jwt
from flask_cors import CORS
from application.celery_init import celery_init_app
from celery.schedules import crontab
from flask_caching import Cache
from application.tasks import monthly_report

cache = Cache()

def create_app():
    app = Flask(__name__)

    app.config['CACHE_TYPE'] = 'RedisCache'
    app.config['CACHE_REDIS_HOST'] = 'localhost'
    app.config['CACHE_REDIS_PORT'] = 6379
    app.config['CACHE_REDIS_DB'] = 0
    app.config['CACHE_DEFAULT_TIMEOUT'] = 300

    app.config.from_object(LocalDevelopmentConfig)

    db.init_app(app)
    jwt.init_app(app)
    CORS(app)
    cache.init_app(app)

    app.app_context().push()

    return app

app = create_app()

celery = celery_init_app(app)
celery.autodiscover_tasks()

@celery.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(
        crontab(minute='*/2'),
        monthly_report.s(),
    )

from application.routes import *

if __name__ == '__main__':
    app.run(debug=True)
