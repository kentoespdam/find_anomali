from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class DetectionResult:
    kategori_anomali: str
    keterangan: str


def detect_row(met_l, met_k, pakai, rata2) -> List[DetectionResult]:
    results: List[DetectionResult] = []

    met_l_f = float(met_l) if met_l is not None else None
    met_k_f = float(met_k) if met_k is not None else None
    pakai_f = float(pakai) if pakai is not None else None
    rata2_f = float(rata2) if rata2 is not None else None

    if met_k_f is not None and met_l_f is not None and met_k_f < met_l_f:
        selisih = met_l_f - met_k_f
        results.append(DetectionResult(
            kategori_anomali="METER_MUNDUR",
            keterangan=f"met_k={met_k_f} < met_l={met_l_f} (selisih={selisih})",
        ))

    return results
