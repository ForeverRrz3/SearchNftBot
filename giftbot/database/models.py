from more_itertools.recipes import unique
from sqlalchemy import String,Float,Text,DateTime,func,Boolean
from sqlalchemy.orm import DeclarativeBase,Mapped,mapped_column

class Base(DeclarativeBase):

    create:Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    update: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

class Gift(Base):
    __tablename__ = "gift"

    id: Mapped[int] = mapped_column(primary_key=True,autoincrement=True)
    name:Mapped[str] = mapped_column(String(30),nullable=False)
    num: Mapped[int] = mapped_column(nullable=False)
    model: Mapped[str] = mapped_column(String(30),nullable=False)
    symbol: Mapped[str] = mapped_column(String(30),nullable=False)
    bg: Mapped[str] = mapped_column(String(30),nullable=False)


class Banner(Base):
    __tablename__ = "banner"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(15), unique=True)
    image: Mapped[str] = mapped_column(String(150), nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)


class Symbol(Base):
    __tablename__ =  "symbol"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(30),unique=True)

class Bg(Base):
    __tablename__ = "bg"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(30), unique=True)

class Admins(Base):
    __tablename__ = "admin"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    admin_id: Mapped[int] = mapped_column(nullable=False,unique=True)
