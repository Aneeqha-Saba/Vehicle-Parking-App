class Config():
    DEBUG = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False 

class LocalDevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///parkingdb.sqlite3' #connects the application with the database
    JWT_SECRET_KEY = 'top-secret-key' #required for the package flask_jwt_extended, it encrypts the data