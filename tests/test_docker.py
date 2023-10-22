import time
import psycopg
import pytest

POSTGRES_PASSWORD = "example"
PORT = 5432
USER = "postgres"
DB = "postgres"


@pytest.fixture(scope="session")
def psql_docker():
    # Set maximum sleep check time for postgres up
    max_checks = 40
    is_pg_up = False
    for _ in range(max_checks):
        try:
            conn = psycopg.connect(
                dbname="postgres",
                user=USER,
                password=POSTGRES_PASSWORD,
                host="127.0.0.1",
                port=PORT,
            )
            conn.close()
            is_pg_up = True
            break
        except psycopg.OperationalError:
            time.sleep(5)

    if not is_pg_up:
        raise ValueError("Could not connect to PostgreSQL server")

    yield

@pytest.fixture(scope="session")
def database(psql_docker):
    yield psycopg.connect(
        dbname=DB,
        user=USER,
        password=POSTGRES_PASSWORD,
        host="127.0.0.1",
        port=PORT,
    )

# test_file.py
from psycopg import sql
from psycopg.rows import dict_row

# just test whether our docker container is up and running and pgvector is working
def test_tables_count(database):
    with database.cursor(row_factory=dict_row) as cursor:
        cursor.execute(
            sql.SQL(
                "CREATE EXTENSION vector;"
            )
        )
        time.sleep(2)
        cursor.execute(
            sql.SQL(
                "CREATE TABLE items (id bigserial PRIMARY KEY, embedding vector(3));"
            )
        )
        time.sleep(2)
        cursor.execute(
            sql.SQL(
                "INSERT INTO items (embedding) VALUES ('[1,2,3]'), ('[4,5,6]');"
            )
        )
        time.sleep(2)
        cursor.execute(
            sql.SQL(
                "SELECT * FROM items ORDER BY embedding <-> '[3,1,2]' LIMIT 5;"
            )
        )
        time.sleep(2)
        result = cursor.fetchall()
        print(result)
    assert 0 == 0