"""Database handler"""

import logging
from os import getenv
from pathlib import Path

import psycopg2
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

# Database connection configuration
db_config = {
    "host": getenv("DB_HOST", "127.0.0.1"),
    "port": getenv("DB_PORT", "5433"),
    "dbname": getenv("DB_NAME", "yugabyte"),
    "user": getenv("DB_USER", "admin"),
    "password": getenv("DB_PASSWORD", "password"),
}


def database_connection():
    """Returns the database connection"""
    try:
        conn = psycopg2.connect(**db_config)
        return conn
    except Exception as e:
        logging.error("Error connecting to database:", e)
        exit(1)


def write_trade_to_db(connection, message, user_id):
    """Write a trade to the database"""
    order_quantity = message["order_quantity"]
    trade_type = message["trade_type"]
    symbol = message["symbol"]
    # trade_time = message['timestamp'] # TODO: should convert timestamp to datetime object instead
    bid_price = message["bid_price"]
    insert_query = f"insert into public.\"Trade\"(user_id, bid_price, order_quantity, trade_time, trade_type, symbol) values ('{user_id}','{bid_price}','{order_quantity}',NOW(),'{trade_type}','{symbol}');"
    conn = connection
    conn.set_session(autocommit=True)
    cur = conn.cursor()
    try:
        cur.execute(insert_query)
        cur.close()
    except Exception as e:
        logging.error("Error executing query", e)
        conn.close()


def init_db():
    """Initialize the database with default schema"""

    # Read table schema from .sql file
    create_sql_schema_query = Path("schema/default_schema.sql").read_text()
    # Uncomment next line if you want to load data from `load_default_data.sql` and not from `seed_user_data.py`
    # load_default_data_query = Path("schema/queries/load_default_data.sql").read_text()

    conn = database_connection()
    logging.info("Connecting to database...")
    conn.set_session(autocommit=True)
    cur = conn.cursor()

    try:
        cur.execute(create_sql_schema_query)
        logging.info("Created table with default schema")
        # Use the following if you want load data from load_default_data.sql and not from `seed_user_data.py`
        # cur.execute(load_default_data_query)
        cur.close()
    except Exception as e:
        logging.error("Error executing query", e)
        conn.close()


if __name__ == "__main__":
    connection = init_db()
    logging.info("Initializing database...")
