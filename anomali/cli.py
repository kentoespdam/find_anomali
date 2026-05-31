from anomali.config import load_config
from anomali.db import load_dataframe
from anomali.detector import detect_row
from anomali.exporter import write_csv


def run() -> None:
    cfg = load_config()

    df = load_dataframe(cfg)
    total = len(df)
    print(f"Total baris diperiksa: {total}")

    anomali_rows = []
    for _, row in df.iterrows():
        detections = detect_row(
            met_l=row.get("met_l"),
            met_k=row.get("met_k"),
            pakai=row.get("pakai"),
            rata2=row.get("rata2"),
        )
        if detections:
            anomali_rows.append({
                "nosamw": row.get("nosamw"),
                "met_l": row.get("met_l"),
                "met_k": row.get("met_k"),
                "pakai": row.get("pakai"),
                "rata2": row.get("rata2"),
                "selisih_meter": (
                    float(row["met_l"]) - float(row["met_k"])
                    if row.get("met_l") is not None and row.get("met_k") is not None
                    else None
                ),
                "selisih_vs_rata2": None,
                "rasio": None,
                "kategori_anomali": ";".join(d.kategori_anomali for d in detections),
                "keterangan": " | ".join(d.keterangan for d in detections),
            })

    import pandas as pd
    result_df = pd.DataFrame(anomali_rows)

    write_csv(result_df, cfg.output_path)
    print(f"Total anomali: {len(result_df)}")
    print(f"Output: {cfg.output_path}")
