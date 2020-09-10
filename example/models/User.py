from db import db
from sqlalchemy import (
    Table,
    Column,
    String,
)

User = Table(
    "users",
    db.metadata,
    Column("id", String, primary_key=True),
    Column("email", String),
    Column("password", String)
)
