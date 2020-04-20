from flask_sqlalchemy import SQLAlchemy


db: SQLAlchemy = SQLAlchemy()


def create():
    db.create_all()
    pass


def reset_database():
    db.drop_all()
    db.create_all()
    pass
