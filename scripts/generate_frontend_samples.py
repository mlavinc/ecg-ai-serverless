"""Generate synthetic per-class ECG samples bundled with the frontend.

These are NOT real PhysioNet recordings -- the raw dataset is not included in
this repository. They are illustrative synthetic waveforms (tuned per class
mostly via heart rate / noise / amplitude) so a visitor without a real WFDB
file can still exercise every code path of the demo ("Try a sample" button).
This is stated explicitly in the frontend UI and in data/frontend_samples/README.

Writes, for each class:
    frontend/public/samples/<id>.hea   (WFDB header, for transparency/download)
    frontend/public/samples/<id>.dat   (WFDB signal)
    frontend/public/samples/<id>.json  ({"header": base64, "signal": base64})
    frontend/public/samples/index.json (catalog consumed by the frontend)
"""

import base64
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.constants import CLASS_NAMES
from backend.utils.mock_ecg import write_mock_record

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "frontend" / "public" / "samples"

# (class_id, heart_rate, noise_std, seed, description)
SAMPLE_SPECS = {
    0: (150, 0.09, 1, "Chaotic, high-frequency oscillation with no discernible QRS-T structure."),
    1: (110, 0.05, 2, "Polymorphic QRS complexes with a twisting amplitude envelope."),
    2: (130, 0.03, 3, "Fast, wide-QRS regular rhythm with reduced RR variability."),
    3: (95, 0.025, 4, "Irregular rhythm with occasional ectopic-like spikes."),
    4: (105, 0.02, 5, "Narrow, regular QRS complexes at an elevated rate, abnormal P-wave timing."),
    5: (72, 0.01, 42, "Regular QRS complexes at a normal rate with stable RR intervals."),
}


def generate_class_signal(heart_rate, noise_std, seed, duration_s=10.0, fs=250):
    rng = np.random.default_rng(seed)
    n_samples = int(duration_s * fs)
    t = np.arange(n_samples) / fs

    baseline = 0.04 * np.sin(2 * np.pi * 0.25 * t)
    noise = rng.normal(0.0, noise_std, size=n_samples)
    signal = baseline + noise

    rr = 60.0 / heart_rate
    qrs_width = 0.02
    beat_time = 0.0
    while beat_time < duration_s:
        center = int(beat_time * fs)
        width = int(qrs_width * fs) or 1
        idx = np.arange(max(0, center - width), min(n_samples, center + width))
        amp = 1.0 + rng.normal(0, 0.15)
        signal[idx] += amp * np.exp(-0.5 * ((idx - center) / (width / 2.0)) ** 2)
        beat_time += rr * (1 + rng.normal(0, 0.03))

    return signal.reshape(-1, 1)


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    catalog = []

    for class_id, (hr, noise, seed, description) in SAMPLE_SPECS.items():
        class_name = CLASS_NAMES[class_id]
        sample_id = class_name.lower()
        record_path = OUTPUT_DIR / sample_id

        import backend.utils.mock_ecg as mock_ecg

        original_generate = mock_ecg.generate_signal
        mock_ecg.generate_signal = lambda **kwargs: generate_class_signal(
            hr, noise, seed, duration_s=kwargs.get("duration_s", 10.0), fs=kwargs.get("fs", 250)
        )
        try:
            write_mock_record(str(record_path), duration_s=10.0, fs=250, seed=seed)
        finally:
            mock_ecg.generate_signal = original_generate

        header_bytes = (record_path.with_suffix(".hea")).read_bytes()
        signal_bytes = (record_path.with_suffix(".dat")).read_bytes()

        payload = {
            "header": base64.b64encode(header_bytes).decode("ascii"),
            "signal": base64.b64encode(signal_bytes).decode("ascii"),
        }
        (record_path.with_suffix(".json")).write_text(json.dumps(payload))

        catalog.append(
            {
                "id": sample_id,
                "label": class_name.replace("_", " "),
                "className": class_name,
                "description": description,
                "file": f"{sample_id}.json",
            }
        )
        print(f"  generated sample: {sample_id}")

    (OUTPUT_DIR / "index.json").write_text(json.dumps(catalog, indent=2))
    print(f"\nWrote {len(catalog)} samples + index.json to {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
