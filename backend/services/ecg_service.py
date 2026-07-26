"""Minimal WFDB reader (format 16 only).

Replaces the ``wfdb`` package, which transitively pulled in matplotlib,
aiohttp, requests, fsspec and soundfile -- far too heavy for a Lambda ZIP.
The PhysioNet ECG Fragment Database records used here are all single-lead,
format-16 (16-bit little-endian) records, which this reader supports.
"""

import os

import numpy as np


def _parse_gain_field(field):
    """Parse the WFDB 'ADCgain(baseline)/units' signal field.

    Returns (gain, baseline_or_None).
    """
    # Drop the optional /units suffix.
    field = field.split("/")[0]

    baseline = None
    if "(" in field:
        gain_str, rest = field.split("(", 1)
        baseline = int(rest.rstrip(")"))
        field = gain_str

    gain = float(field) if field else 200.0
    return gain, baseline


def _parse_header_lines(lines):
    """Parse the lines of a WFDB .hea header into a small dict."""
    lines = [ln.strip() for ln in lines if ln.strip() and not ln.startswith("#")]

    # Record line: <name> <nsig> <fs> <nsamples>
    rec = lines[0].split()
    n_sig = int(rec[1])

    signals = []
    for spec in lines[1 : 1 + n_sig]:
        tok = spec.split()
        filename = tok[0]
        fmt = tok[1]
        gain, baseline = _parse_gain_field(tok[2]) if len(tok) > 2 else (200.0, None)
        adc_zero = int(tok[4]) if len(tok) > 4 else 0
        if baseline is None:
            baseline = adc_zero
        signals.append(
            {
                "filename": filename,
                "fmt": fmt,
                "gain": gain,
                "baseline": baseline,
            }
        )

    return {"n_sig": n_sig, "signals": signals}


def _decode_signal(header, raw_bytes):
    """Turn raw format-16 bytes + a parsed header into a physical signal."""
    n_sig = header["n_sig"]

    first = header["signals"][0]
    fmt = first["fmt"]
    if fmt != "16":
        raise ValueError(
            f"Unsupported WFDB format '{fmt}' (only format 16 is supported)."
        )

    raw = np.frombuffer(raw_bytes, dtype="<i2").astype(np.float64)
    if raw.size == 0 or raw.size % n_sig != 0:
        raise ValueError(
            "Malformed ECG signal file: sample count is not a multiple of "
            f"the declared channel count ({n_sig})."
        )

    # De-interleave channels and apply per-channel calibration.
    raw = raw.reshape(-1, n_sig)
    p_signal = np.empty_like(raw)
    for i, sig in enumerate(header["signals"]):
        p_signal[:, i] = (raw[:, i] - sig["baseline"]) / sig["gain"]

    return p_signal


def load_ecg(record_path):
    """Read a WFDB record (base path, no extension) into a physical signal.

    Returns a float ndarray of shape (n_samples, n_sig), matching the layout
    previously returned by ``wfdb.rdrecord(...).p_signal``.
    """
    record_path = str(record_path)
    hea_path = record_path + ".hea"

    with open(hea_path, "r") as fh:
        header = _parse_header_lines(fh.readlines())

    base_dir = os.path.dirname(hea_path)
    dat_path = os.path.join(base_dir, header["signals"][0]["filename"])
    with open(dat_path, "rb") as fh:
        raw_bytes = fh.read()

    return _decode_signal(header, raw_bytes)


def load_ecg_from_bytes(header_bytes, signal_bytes):
    """Read a WFDB record given in-memory header (.hea) and signal (.dat) bytes.

    Used by the HTTP handler, which receives file contents over the wire
    instead of a filesystem path.
    """
    text = header_bytes.decode("ascii", errors="ignore")
    header = _parse_header_lines(text.splitlines())
    return _decode_signal(header, signal_bytes)
