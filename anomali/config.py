import os
from dataclasses import dataclass, field
from dotenv import load_dotenv


@dataclass
class Config:
    db_host: str = "localhost"
    db_port: int = 3306
    db_user: str = "root"
    db_password: str = ""
    db_name: str = "rekairnow"
    db_table: str = "rekairnow"
    output_path: str = "anomali.csv"


def load_config() -> Config:
    load_dotenv()
    return Config(
        db_host=os.getenv("DB_HOST", "localhost"),
        db_port=int(os.getenv("DB_PORT", "3306")),
        db_user=os.getenv("DB_USER", "root"),
        db_password=os.getenv("DB_PASSWORD", ""),
        db_name=os.getenv("DB_NAME", "rekairnow"),
        db_table=os.getenv("DB_TABLE", "rekairnow"),
        output_path=os.getenv("OUTPUT_PATH", "anomali.csv"),
    )
