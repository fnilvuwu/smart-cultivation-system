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
from datetime import datetime
from werkzeug.security import generate_password_hash

db = SQLAlchemy()


def init_db(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()


def drop_db(app):
    with app.app_context():
        db.reflect()
        db.drop_all()


def populate_db(app):
    with app.app_context():
        from database.model.user import User
        from database.model.pond import Pond, WaterQuality, FishData, FishPondMetrics
        from database.model.employee import Employee

        # Create default owner
        owner = User.query.filter_by(email="owner1@example.com").first()
        if not owner:
            owner = User(
                email="owner1@example.com",
                username="owner1",
                password="owner_password",
            )
            db.session.add(owner)
            db.session.commit()

        # Create dummy ponds
        ponds = [
            {"pond_name": "Pond A", "location": "Location A", "owner_id": owner.user_id},
            {"pond_name": "Pond B", "location": "Location B", "owner_id": owner.user_id},
        ]
        pond_instances = [Pond(**pond) for pond in ponds]
        db.session.add_all(pond_instances)
        db.session.commit()

        # Retrieve pond IDs
        pond_ids = [pond.pond_id for pond in pond_instances]

        # Create dummy employees
        employees = [
            {"employee_name": "Employee One", "employee_email": "employee1@example.com", "password": "emp_password1"},
            {"employee_name": "Employee Two", "employee_email": "employee2@example.com", "password": "emp_password2"},
        ]
        employee_instances = [
            Employee(
                user_id=owner.user_id,
                employee_name=emp["employee_name"],
                employee_email=emp["employee_email"],
                password=emp["password"],
            )
            for emp in employees
        ]
        db.session.add_all(employee_instances)
        db.session.commit()

        # Assign employees to ponds
        for i, employee in enumerate(employee_instances):
            pond = Pond.query.get(pond_ids[i % len(pond_ids)])  # Assign to ponds in round-robin
            pond.employees.append(employee)
        db.session.commit()

        # Create FishData records
        fish_data = [
            {"pond_id": pond_ids[0], "fish_weight": 1.5, "fish_height": 10.0, "fish_population": 100, "date": datetime(2024, 7, 31, 8, 0, 0), "employee_id": employee_instances[0].employee_id},
            {"pond_id": pond_ids[0], "fish_weight": 1.6, "fish_height": 10.5, "fish_population": 105, "date": datetime(2024, 7, 31, 12, 0, 0), "employee_id": employee_instances[0].employee_id},
            {"pond_id": pond_ids[1], "fish_weight": 2.0, "fish_height": 12.0, "fish_population": 150, "date": datetime(2024, 7, 31, 8, 0, 0), "employee_id": employee_instances[1].employee_id},
            {"pond_id": pond_ids[1], "fish_weight": 2.1, "fish_height": 12.5, "fish_population": 155, "date": datetime(2024, 7, 31, 12, 0, 0), "employee_id": employee_instances[1].employee_id},
        ]
        fish_data_instances = [FishData(**fish) for fish in fish_data]
        db.session.add_all(fish_data_instances)
        db.session.commit()

        # Create WaterQuality records

        water_qualities = [
            {"pond_id": pond_ids[0], "pH": 7.0, "turbidity": 5.0, "temperature": 25.0, "nitrate": 10.0, 'ammonia': 0, "dissolved_oxygen": 0, "date": datetime(2024, 8, 30, 8, 0, 0), "employee_id": employee_instances[0].employee_id},
            {"pond_id": pond_ids[0], "pH": 7.1, "turbidity": 4.5, "temperature": 26.0, "nitrate": 9.5, 'ammonia': 0.5, "dissolved_oxygen": 5, "date": datetime(2024, 9, 30, 8, 0, 0), "employee_id": employee_instances[0].employee_id},
            {"pond_id": pond_ids[1], "pH": 6.5, "turbidity": 10.0, "temperature": 22.0, "nitrate": 5.0, 'ammonia': 0.7, "dissolved_oxygen": 10, "date": datetime(2024, 10, 30, 8, 0, 0), "employee_id": employee_instances[1].employee_id},
            {"pond_id": pond_ids[1], "pH": 6.6, "turbidity": 9.5, "temperature": 22.5, "nitrate": 5.2, 'ammonia': 0.01, "dissolved_oxygen": 15, "date": datetime(2024, 11, 30, 8, 0, 0), "employee_id": employee_instances[1].employee_id},
        ]
        water_quality_instances = [WaterQuality(**quality) for quality in water_qualities]
        db.session.add_all(water_quality_instances)
        db.session.commit()

        # Create FishPondMetrics records
        metrics = [
            {
                "pond_id": pond_ids[0],
                "total_fish_weight": 1.5 * 100 + 1.6 * 105,
                "average_fish_weight": (1.5 + 1.6) / 2,
                "average_fish_height": (10.0 + 10.5) / 2,
                "total_population": 100 + 105,
            },
            {
                "pond_id": pond_ids[1],
                "total_fish_weight": 2.0 * 150 + 2.1 * 155,
                "average_fish_weight": (2.0 + 2.1) / 2,
                "average_fish_height": (12.0 + 12.5) / 2,
                "total_population": 150 + 155,
            },
        ]
        metric_instances = [FishPondMetrics(**metric) for metric in metrics]
        db.session.add_all(metric_instances)
        db.session.commit()


def format_database_error(exception):
    if isinstance(exception, IntegrityError):
        return f"Integrity constraint violation: {exception.orig}"
    elif isinstance(exception, OperationalError):
        return f"Database operation error: {exception.orig}"
    elif isinstance(exception, ProgrammingError):
        return f"Database programming error: {exception.orig}"
    elif isinstance(exception, DataError):
        return f"Data error: {exception.orig}"
    elif isinstance(exception, NoResultFound):
        return "No result found"
    elif isinstance(exception, MultipleResultsFound):
        return "Multiple results found"
    else:
        return f"Unexpected error: {exception}"


@click.command(name="init-db")
@with_appcontext
def init_db_command():
    try:
        init_db(current_app)
        click.echo("Database tables created.")
    except Exception as e:
        click.echo(f"Error creating database tables: {format_database_error(e)}")


@click.command(name="drop-db")
@with_appcontext
def drop_db_command():
    try:
        drop_db(current_app)
        click.echo("Database tables dropped.")
    except Exception as e:
        click.echo(f"Error dropping database tables: {format_database_error(e)}")


@click.command(name="populate-db")
@with_appcontext
def populate_db_command():
    try:
        populate_db(current_app)
        click.echo("Database populated.")
    except Exception as e:
        click.echo(f"Error populating database: {format_database_error(e)}")


def register_commands(app):
    app.cli.add_command(init_db_command)
    app.cli.add_command(drop_db_command)
    app.cli.add_command(populate_db_command)
