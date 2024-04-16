"""Data models."""
from rest.app import db
import datetime
import pandas as pd

from typing_extensions import Annotated
from typing import Optional
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.inspection import inspect
from sqlalchemy import func

timestamp = Annotated[
    datetime.datetime,
    mapped_column(nullable=False, server_default=func.now()),
]


class Serializer(object):
    def serialize(self):
        return {c: getattr(self, c) for c in inspect(self).attrs.keys()}
    @staticmethod
    def serialize_list(l):
        return [m.serialize() for m in l]

class Image(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    fullpath: Mapped[str] = mapped_column(unique=False)
    content: Mapped[str]
    time_created: Mapped[Optional[datetime.datetime]]
    time_updated: Mapped[Optional[datetime.datetime]]

    def serialize(self):
        d = Serializer.serialize(self)
        return d
    

