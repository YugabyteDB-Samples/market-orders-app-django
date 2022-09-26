"""Utility for creating and inserting user data into the database"""
# from .utils import insert_user_data_to_db
import logging

from faker import Faker

from market_orders.models import User2


def insert_user_data_to_db(NO_OF_USERS_TO_CREATE=3):
    """Insert initial user data into the database"""
    fake = Faker()
    for user_count in range(NO_OF_USERS_TO_CREATE):
        first_name = fake.unique.first_name()
        last_name = fake.unique.last_name()
        email = f"{(first_name + last_name).lower()}@example.com"
        try:
            user = User2(
                first_name=first_name, last_name=last_name, email=email, name=first_name
            )
            user.save()
            print("Added initial user")
        except Exception as e:
            logging.error("Error executing query", e)


def run():
    # ref: https://django-extensions.readthedocs.io/en/latest/runscript.html#getting-started
    insert_user_data_to_db()
