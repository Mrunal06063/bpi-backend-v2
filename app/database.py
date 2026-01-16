from sqlalchemy import create_engine

DATABASE_URL = "postgresql://user:password@localhost:5432/bpi_db"

engine = create_engine(DATABASE_URL)
    