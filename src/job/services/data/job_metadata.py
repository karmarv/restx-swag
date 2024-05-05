"""Data models."""
import os
import datetime
from typing_extensions import Annotated
from typing import Optional
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import func, select

from job import db
from job.services import config
from job.services.data import Serializer

timestamp = Annotated[
    datetime.datetime,
    mapped_column(nullable=False, server_default=func.now()),
]

# ------------------ #
# Data Model Objects #
# ------------------ #
class JobMetadata(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=False)
    type: Mapped[str] = mapped_column(unique=False)
    data: Mapped[str] = mapped_column(unique=False)
    path: Mapped[str] = mapped_column(unique=False, nullable=True)
    status: Mapped[Optional[str]]
    result: Mapped[Optional[str]]
    content_type: Mapped[Optional[str]]
    time_created: Mapped[Optional[datetime.datetime]]
    time_updated: Mapped[Optional[datetime.datetime]]

    def serialize(self):
        d = Serializer.serialize(self)
        return d



# ------------------- #
# Data Access Objects #
# ------------------- #
# Create an entry into the imagetable
def create_job_metadata(name, type, data, path, overwrite=False):
    new_job = None
    exists = JobMetadata.query.filter(JobMetadata.name==name).first()
    if exists and not overwrite:
        print("Job already exists: ", exists)
        return exists.serialize()
    else:    
        new_job = JobMetadata(
            name=name,
            type=type,
            data=data,
            path=path,
            status=config.REDIS_JOB_STATUS[0],
        )  # Create an instance of the Job class
        db.session.add(new_job)     # Adds new User record to database
        db.session.commit()         # Commits all changes
    return new_job.serialize()

# Read entries from job metadata table
def read_job_metadata(id=None, name=None):
    # check for filename match in query
    if id is not None:
        jobs = JobMetadata.query.filter(JobMetadata.id==id).first()
    elif name is not None:
        jobs = JobMetadata.query.filter(JobMetadata.name.like(f'%{name}%')).all()
    else:
        jobs = JobMetadata.query.all()
    return Serializer.serialize_list(jobs)
