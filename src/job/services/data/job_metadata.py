"""Data models."""
import os
import datetime
from typing_extensions import Annotated
from typing import Optional
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import func, select
from sqlalchemy import JSON

from job import db
from job.services import config
from job.services.data import Serializer
from job.services.exceptions import JobException


# ------------------ #
# Data Model Objects #
# ------------------ #
class JobMetadata(db.Model):
    id      : Mapped[int] = mapped_column(primary_key=True)
    module  : Mapped[str] = mapped_column(unique=False)
    queue   : Mapped[str] = mapped_column(unique=False)
    data    : Mapped[str] = mapped_column(unique=False)
    path    : Mapped[str] = mapped_column(unique=False, nullable=True)
    status  : Mapped[Optional[str]]
    tag     : Mapped[Optional[str]]
    result  : Mapped[Optional[JSON]] = mapped_column(type_=JSON)
    time_created: Mapped[Optional[datetime.datetime]] = mapped_column(nullable=False, server_default=func.CURRENT_TIMESTAMP())
    time_updated: Mapped[Optional[datetime.datetime]] = mapped_column(nullable=False, server_default=func.CURRENT_TIMESTAMP())

    def serialize(self):
        d = Serializer.serialize(self)
        return d



# ------------------- #
# Data Access Objects #
# ------------------- #

def create_job_metadata(module, queue, data, path, tag):
    """Create an entry into the job table"""
    new_job = JobMetadata(
        module=module,
        queue=queue,
        data=data,
        path=path,
        status=config.REDIS_JOB_STATUS[0],
        tag=tag
    )  # Create an instance of the Job class
    db.session.add(new_job)     # Adds new User record to database
    db.session.commit()         # Commits all changes
    return new_job.serialize()

def read_job_metadata(id=None, module=None):
    """Read entries from job metadata table"""
    # check for filename match in query
    if id is not None:
        job = JobMetadata.query.filter(JobMetadata.id==id).first()
        return job.serialize()
    elif module is not None:
        jobs = JobMetadata.query.filter(JobMetadata.module.like(f'%{module}%')).all()
        return Serializer.serialize_list(jobs)
    else:
        jobs = JobMetadata.query.all()
        return Serializer.serialize_list(jobs)

def delete_job_metadata(job_id):
    """Delete an entry from job metadata table"""
    obj = JobMetadata.query.filter(JobMetadata.id==job_id).one()
    db.session.delete(obj)
    db.session.commit()
    return
