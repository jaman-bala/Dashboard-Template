from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String


from src.core.database.database import Base


class StatementOrm(Base):
    __tablename__ = "statements"

    title: Mapped[str] = mapped_column(String(200), nullable=False)
