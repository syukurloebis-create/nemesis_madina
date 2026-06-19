import pandas as pd
from sqlalchemy import create_engine

sqlite = create_engine(
    "sqlite:////home/.../rup_database.db"
)

postgres = create_engine(
    "postgresql://nemesis:nemesis123@localhost:5432/nemesis_db"
)

df = pd.read_sql(
    "SELECT * FROM rup_paket",
    sqlite
)

df.to_sql(
    "rup_paket",
    postgres,
    if_exists="append",
    index=False
)

print("Imported:", len(df))