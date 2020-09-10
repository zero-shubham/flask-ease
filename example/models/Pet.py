from db import db
from sqlalchemy import (
    Table,
    Column,
    String,
    ForeignKey
)

Pet = Table(
    "pets",
    db.metadata,
    Column("id", String, primary_key=True),
    Column("name", String),
    Column("breed", String),
    Column("description", String),
    Column(
        "owner",
        ForeignKey("users.id")
    )
)
