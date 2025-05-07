import uuid, datetime as dt
from sqlalchemy import String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from models.base import Base

class SessionToken(Base):
    __tablename__ = "session_tokens"

    token:      Mapped[str] = mapped_column(String, primary_key=True)
    user_id:    Mapped[int] = mapped_column(ForeignKey("users.id"))
    expires_at: Mapped[dt.datetime] = mapped_column(DateTime)
