import os

import pytest
from sqlalchemy import text

TEST_DATABASE_URL = (
    "postgresql://postgres:postgres@localhost:5432/"
    "public_service_navigator_test"
)

# IMPORTANT:
# Set the test database before importing the application database module.
os.environ["DATABASE_URL"] = TEST_DATABASE_URL

from app.db import database
import app.models


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    # Enable pgvector in the test database.
    with database.engine.begin() as connection:
        connection.execute(
            text("CREATE EXTENSION IF NOT EXISTS vector")
        )

    # Create all application tables in the test database.
    database.Base.metadata.create_all(
        bind=database.engine
    )

    yield

    # Remove test tables after the test session.
    database.Base.metadata.drop_all(
        bind=database.engine
    )

    database.engine.dispose()