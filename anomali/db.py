import mysql.connector
import pandas as pd

from anomali.config import Config


def load_dataframe(cfg: Config) -> pd.DataFrame:
    conn = mysql.connector.connect(
        host=cfg.db_host,
        port=cfg.db_port,
        user=cfg.db_user,
        password=cfg.db_password,
        database=cfg.db_name,
    )
    query = f"SELECT nosamw, met_l, met_k, pakai, rata2 FROM {cfg.db_table}"
    df = pd.read_sql(query, conn)
    conn.close()
    return df
