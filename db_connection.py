import psycopg2
from psycopg2.extras import RealDictCursor

def get_connection():
    return psycopg2.connect(
        host="localhost",
        port=5432,
        dbname="my_database",
        user="postgres",
        password="S@hil786"
    )