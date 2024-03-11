import asyncio
import os
from typing import Union

import asyncpg
from asyncpg import Connection, Pool
from dotenv import load_dotenv
from passlib.hash import pbkdf2_sha256
from pydantic import BaseModel

load_dotenv(dotenv_path='.venv/.env')

PGHOST = os.getenv('PGHOST')
PGUSER = os.getenv('PGUSER')
PGPORT = os.getenv('PGPORT')
PGDATABASE = os.getenv('PGDATABASE')
PGPASSWORD = os.getenv('PGPASSWORD')


class User:
    def __init__(self, id, email, password, email_verified):
        self.id = id
        self.email = email
        self.password = password
        self.email_verified = email_verified


async def init_db() -> Pool:
    """
    Asynchronously initializes the database connection.

    Attempts to establish a connection to the database using the provided credentials.
    If successful, returns the connection object. If the connection fails, raises a ConnectionError.

    Returns:
        asyncpg.Connection: The database connection object.

    Raises:
        ConnectionError: If the connection to the database fails.
    """
    try:
        # Establish a connection to the database
        return await asyncpg.create_pool(
            user=PGUSER, password=PGPASSWORD, host=PGHOST, port=PGPORT, database=PGDATABASE, ssl=True
        )
    except asyncpg.PostgresError as e:
        # Handle the exception and raise a ConnectionError
        raise ConnectionError("Failed to connect to the database.") from e


async def get_user(db: Pool, email: str):
    async with db.acquire() as connection:
        query = "SELECT id, email, password, email_verified FROM users WHERE email = $1"
        row = await connection.fetchrow(query, email)
        if row:
            return User(row['id'], row['email'], row['password'], row['email_verified'])
        else:
            return None


async def authenticate_user(email: str, password: str):
    conn: Pool = await init_db()
    user = await get_user(conn, email)
    if not user:
        return False

    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, pbkdf2_sha256.verify, password, user.password)
    if not result:
        return False

    return user.email
