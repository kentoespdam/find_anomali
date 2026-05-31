import pytest

from anomali.detector import detect_row


def test_meter_mundur_detected():
    results = detect_row(met_l=200, met_k=150, pakai=50, rata2=45)
    kategories = [r.kategori_anomali for r in results]
    assert "METER_MUNDUR" in kategories


def test_normal_row_no_anomaly():
    results = detect_row(met_l=100, met_k=200, pakai=100, rata2=95)
    assert len(results) == 0


@pytest.mark.parametrize("met_l,met_k", [
    (150, 100),
    (100, 50),
    (500, 250),
])
def test_meter_mundur_parametrized(met_l, met_k):
    results = detect_row(met_l=met_l, met_k=met_k, pakai=0, rata2=0)
    kategories = [r.kategori_anomali for r in results]
    assert "METER_MUNDUR" in kategories


def test_meter_normal_no_flag():
    results = detect_row(met_l=100, met_k=200, pakai=100, rata2=50)
    assert len(results) == 0
