"""Data models."""
import os
import datetime
from rest import db

from typing_extensions import Annotated
from typing import Optional
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import func, select

from rest.services.data import Serializer

timestamp = Annotated[
    datetime.datetime,
    mapped_column(nullable=False, server_default=func.now()),
]

# ------------------ #
# Data Model Objects #
# ------------------ #


class ImageMetadata(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=False)
    path: Mapped[str] = mapped_column(unique=False)
    content_type: Mapped[str]
    time_created: Mapped[Optional[datetime.datetime]]
    time_updated: Mapped[Optional[datetime.datetime]]

    def serialize(self):
        d = Serializer.serialize(self)
        return d

# ------------------- #
# Data Access Objects #
# ------------------- #
    
# Create an entry into the imagetable
def create_image_metadata(filename, content, overwrite=False):
    new_img = None
    if filename:
        exists = ImageMetadata.query.filter(ImageMetadata.name == os.path.basename(filename)).first()
        if exists and not overwrite:
            print("Image already exists: ", exists)
            return exists.serialize()
        else:    
            new_img = ImageMetadata(
                name=os.path.basename(filename),
                path=filename,
                content_type=content,
            )  # Create an instance of the Image class
            db.session.add(new_img)     # Adds new User record to database
            db.session.commit()         # Commits all changes
    return new_img.serialize()

# Read entries from images table
def read_image_metadata(filename=None):
    # check for filename match in query
    if filename is not None:
        imgs = ImageMetadata.query.filter(ImageMetadata.name.like(f'%{os.path.basename(filename)}%')).all()
    else:
        imgs = ImageMetadata.query.all()
    return Serializer.serialize_list(imgs)
    

