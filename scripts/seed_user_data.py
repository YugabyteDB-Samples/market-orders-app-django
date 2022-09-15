"""Utility for creating and inserting user data into the database"""
import logging

from faker import Faker

from db import database_connection

fake = Faker()


def insert_user_data_to_db():
    """Insert initial user data into the database"""
    insert_query = 'INSERT INTO public."User"(first_name, last_name, email) VALUES '
    query_bind_values = ""
    for user_count in range(5):
        first_name = fake.unique.first_name()
        last_name = fake.unique.last_name()
        email = f"{(first_name + last_name).lower()}@example.com"
        if user_count < 1:
            query_bind_values = f"('{first_name}','{last_name}','{email}')"
        else:
            query_bind_values = "".join(
                [query_bind_values, "," f"('{first_name}','{last_name}','{email}')"]
            )
    insert_query = "".join([insert_query, query_bind_values])
    conn = database_connection()
    conn.set_session(autocommit=True)
    cur = conn.cursor()
    try:
        cur.execute(insert_query)
        cur.close()
    except Exception as e:
        logging.error("Error executing query", e)
        conn.close()


if __name__ == "__main__":
    insert_user_data_to_db()
