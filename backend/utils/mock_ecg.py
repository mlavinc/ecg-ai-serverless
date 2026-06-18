"""Synthetic ECG generator for local testing.

Writes a minimal WFDB *format 16* record (.hea / .dat) on disk so the full
inference pipeline -- including the lightweight reader in ecg_service -- can
run locally without the real ECG_DB dataset. No third-party dependency is
required (matches the dependency-free reader used at inference time).
"""

import os

import numpy as np


FS = 250          # sampling rate (Hz)
ADC_GAIN = 200    # ADC units per mV (matches the ECG_DB records)
ADC_ZERO = 0


def generate_signal(duration_s=10.0, fs=FS, heart_rate=72, seed=42):
    """Return a synthetic single-lead ECG as a (n_samples, 1) float array."""
    rng = np.random.default_rng(seed)

    n_samples = int(duration_s * fs)
    t = np.arange(n_samples) / fs

    baseline = 0.05 * np.sin(2 * np.pi * 0.3 * t)
    noise = rng.normal(0.0, 0.01, size=n_samples)
    signal = baseline + noise

    # QRS-like spikes at the given heart rate.
    rr = 60.0 / heart_rate
    qrs_width = 0.02
    beat_time = 0.0
    while beat_time < duration_s:
        center = int(beat_time * fs)
        width = int(qrs_width * fs) or 1
        idx = np.arange(max(0, center - width), min(n_samples, center + width))
        signal[idx] += np.exp(-0.5 * ((idx - center) / (width / 2.0)) ** 2)
        beat_time += rr

    return signal.reshape(-1, 1)


def write_mock_record(record_path, duration_s=10.0, fs=FS, seed=42):
    """Write a synthetic WFDB format-16 record; return its base path."""
    record_path = os.path.normpath(record_path)
    write_dir = os.path.dirname(record_path) or "."
    record_name = os.path.basename(record_path)
    os.makedirs(write_dir, exist_ok=True)

    p_signal = generate_signal(duration_s=duration_s, fs=fs, seed=seed)
    n_samples = p_signal.shape[0]

    # Physical -> digital (format 16, little-endian int16).
    d_signal = np.round(p_signal[:, 0] * ADC_GAIN + ADC_ZERO).astype("<i2")
    dat_name = record_name + ".dat"
    d_signal.tofile(os.path.join(write_dir, dat_name))

    init_value = int(d_signal[0])
    checksum = int(np.sum(d_signal.astype(np.int64)) % 65536)
    if checksum >= 32768:
        checksum -= 65536

    header = (
        f"{record_name} 1 {fs} {n_samples}\n"
        f"{dat_name} 16 {ADC_GAIN} 16 {ADC_ZERO} "
        f"{init_value} {checksum} 0 ECG\n"
    )
    with open(os.path.join(write_dir, record_name + ".hea"), "w") as fh:
        fh.write(header)

    return record_path


def ensure_mock_record(record_path):
    """Create the mock record if it does not already exist; return base path."""
    if not os.path.exists(record_path + ".hea"):
        write_mock_record(record_path)
    return record_path
