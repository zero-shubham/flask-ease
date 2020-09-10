from db import db
from sqlalchemy import (
    Table,
    Column,
    ForeignKey,
    String
)

Match = Table(
    "matchs",
    db.metadata,
    Column("id", String, primary_key=True),
    Column("match_1", ForeignKey("pets.id")),
    Column("match_2", ForeignKey("pets.id"))
)
