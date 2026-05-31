import pandas as pd


CSV_SCHEMA = [
    "nosamw", "met_l", "met_k", "pakai", "rata2",
    "selisih_meter", "selisih_vs_rata2", "rasio",
    "kategori_anomali", "keterangan",
]


def write_csv(df: pd.DataFrame, path: str) -> None:
    df[CSV_SCHEMA].to_csv(path, index=False)
