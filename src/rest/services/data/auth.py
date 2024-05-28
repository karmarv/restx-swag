"""Data models."""
import datetime
from typing import List, Optional
from sqlalchemy import func, select
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped, mapped_column
from werkzeug.security import generate_password_hash



from rest import db
from rest.services.data import Serializer
from rest.services.exceptions import ValidationException


# ------------------ #
# Data Model Objects #
# ------------------ #

class User(db.Model): # Parent
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    password_hash: Mapped[str] = mapped_column(unique=True)
    time_created: Mapped[Optional[datetime.datetime]] = mapped_column(nullable=False, server_default=func.CURRENT_TIMESTAMP())
    time_updated: Mapped[Optional[datetime.datetime]] = mapped_column(nullable=False, server_default=func.CURRENT_TIMESTAMP())

    # relationship reference: https://docs.sqlalchemy.org/en/20/orm/basic_relationships.html#one-to-many
    refresh_tokens: Mapped[List["RefreshToken"]] = relationship()

    @property
    def password(self):
        raise AttributeError('Password not readable')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def serialize(self):
        d = Serializer.serialize(self)
        return d

class RefreshToken(db.Model): # Child
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'))
    refresh_token: Mapped[str] = mapped_column(unique=True)
    user_agent_hash: Mapped[str] = mapped_column(unique=True)
    time_created: Mapped[Optional[datetime.datetime]] = mapped_column(nullable=False, server_default=func.CURRENT_TIMESTAMP())
    time_updated: Mapped[Optional[datetime.datetime]] = mapped_column(nullable=False, server_default=func.CURRENT_TIMESTAMP())

    def serialize(self):
        d = Serializer.serialize(self)
        return d

# ------------------- #
# Data Access Objects #
# ------------------- #
    
def create_user(username, password):
    """Create an entry into the user table"""
    if User.query.filter_by(username=username).first():
        raise ValidationException(error_field_name='username', message='This username is already exists')
    user = User(username=username, password=password)
    db.session.add(user)
    db.session.commit()
    return user

def read_user(username):
    return User.query.filter_by(username=username).first()

def current_user(user_id):
    return User.query.get(user_id)


def create_refresh_token(user_id, user_agent_hash, _refresh_token):
    refresh_token = RefreshToken.query.filter_by(user_agent_hash=user_agent_hash).first()

    if not refresh_token:
        refresh_token = RefreshToken(user_id=user_id, refresh_token=_refresh_token,
                                        user_agent_hash=user_agent_hash)
    else:
        refresh_token.refresh_token = _refresh_token

    db.session.add(refresh_token)
    db.session.commit()
    return refresh_token

def read_refresh_token(user_id, refresh_token):
    return RefreshToken.query.filter_by(user_id=user_id, refresh_token=refresh_token).first()

def update_refresh_token(refresh_token):
    db.session.add(refresh_token)
    db.session.commit()
    return refresh_token