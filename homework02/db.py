from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


Base = declarative_base()

engine = create_engine(
    "sqlite:///news.db",
    pool_pre_ping=True,
)

session = sessionmaker(
    bind=engine,
    expire_on_commit=False,
)


class News(Base):
    __tablename__ = "news"

    id = Column(Integer, primary_key=True)
    title = Column(String)
    author = Column(String)
    url = Column(String)
    complexity = Column(String)
    habr_id = Column(String)
    label = Column(String)


Base.metadata.create_all(bind=engine)
