import os
from datetime import datetime
from sqlalchemy import func, ForeignKey
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base, Mapped, mapped_column, relationship
from dotenv import load_dotenv

load_dotenv("../.env")

DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_USER = os.getenv("DB_USER")
DB_NAME = os.getenv("DB_NAME")

URL_DB = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@localhost:5432/{DB_NAME}"


engine = create_async_engine(URL_DB, echo=True)
async_session_maker = async_sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)


async def get_db():
    async with async_session_maker() as session:
        yield session


Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(nullable=False)
    last_name: Mapped[str] = mapped_column(nullable=False)
    email: Mapped[str] = mapped_column(unique=True, nullable=False)
    date_registration: Mapped[datetime] = mapped_column(server_default=func.now())
    transactions: Mapped[list["Transaction"]] = relationship(back_populates="user")


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True)
    status: Mapped[bool] = mapped_column(nullable=False)
    type: Mapped[str] = mapped_column(nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    date_registration: Mapped[datetime] = mapped_column(server_default=func.now())
    user: Mapped["User"] = relationship(back_populates="transactions")

