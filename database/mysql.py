from flask import current_app
from flask_sqlalchemy import SQLAlchemy
import click
from flask.cli import with_appcontext

from sqlalchemy.exc import (
    IntegrityError,
    OperationalError,
    ProgrammingError,
    DataError,
    NoResultFound,
    MultipleResultsFound,
)

db = SQLAlchemy()


def init_db(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()


def drop_db(app):
    with app.app_context():
        db.reflect()
        db.drop_all()


def format_database_error(exception):
    if isinstance(exception, IntegrityError):
        return "Integrity constraint violation: {}".format(exception.orig)
    elif isinstance(exception, OperationalError):
        return "Database operation error: {}".format(exception.orig)
    elif isinstance(exception, ProgrammingError):
        return "Database programming error: {}".format(exception.orig)
    elif isinstance(exception, DataError):
        return "Data error: {}".format(exception.orig)
    elif isinstance(exception, NoResultFound):
        return "No result found: {}".format(exception.orig)
    elif isinstance(exception, MultipleResultsFound):
        return "Multiple results found: {}".format(exception.orig)
    else:
        return "Unknown database error: {}".format(exception)


@click.command("init-db")
@with_appcontext
def init_db_command():
    init_db(current_app)
    click.echo("Initialized the database.")


@click.command("drop-db")
@with_appcontext
def drop_db_command():
    drop_db(current_app)
    click.echo("Dropped the database.")
