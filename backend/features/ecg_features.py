import numpy as np

from scipy.stats import skew
from scipy.stats import kurtosis
from scipy.fft import fft
from scipy.signal import find_peaks, butter, filtfilt


SAMPLING_RATE = 250


def detect_r_peaks(signal_flat, sampling_rate=SAMPLING_RATE):
    """Pan-Tompkins-style R-peak detector using only scipy.

    Replaces the previous neurokit2 dependency (which pulled in matplotlib)
    with scipy, which is already required by scikit-learn -- so it adds
    nothing to the deployment size. A 5-15 Hz band-pass isolates the QRS
    energy and squaring emphasises the R waves regardless of polarity,
    which gives cleaner RR intervals than a raw amplitude threshold.

    The feature *values* differ from the neurokit2 version, so the model is
    retrained on these features to keep training and inference coherent.
    """
    min_distance = max(1, int(0.25 * sampling_rate))  # up to ~240 bpm

    nyq = 0.5 * sampling_rate
    low, high = 5.0 / nyq, 15.0 / nyq
    b, a = butter(2, [low, high], btype="band")

    # filtfilt needs enough samples; fall back to the raw signal otherwise.
    if len(signal_flat) > 3 * (max(len(a), len(b)) + 1):
        filtered = filtfilt(b, a, signal_flat)
    else:
        filtered = signal_flat - np.mean(signal_flat)

    energy = filtered ** 2
    threshold = np.mean(energy) + 0.5 * np.std(energy)

    peaks, _ = find_peaks(energy, distance=min_distance, height=threshold)
    return peaks


def extract_features(signal):
    """
    Extract statistical, HRV and frequency-domain features from ECG signal.
    """

    signal_flat = signal.flatten()

    # =====================================
    # Statistical features
    # =====================================

    mean = np.mean(signal_flat)
    median = np.median(signal_flat)

    std = np.std(signal_flat)
    variance = np.var(signal_flat)

    min_value = np.min(signal_flat)
    max_value = np.max(signal_flat)

    value_range = max_value - min_value

    rms = np.sqrt(np.mean(signal_flat ** 2))

    energy = np.sum(signal_flat ** 2)

    peak_to_peak = np.ptp(signal_flat)

    signal_length = len(signal_flat)

    waveform_length = np.sum(
        np.abs(np.diff(signal_flat))
    )
    signal_skewness = skew(signal_flat)
    signal_kurtosis = kurtosis(signal_flat)

    # =====================================
    # HRV Features
    # =====================================

    mean_rr = 0.0
    std_rr = 0.0
    rmssd = 0.0

    min_rr = 0.0
    max_rr = 0.0
    rr_range = 0.0

    try:

        peaks = detect_r_peaks(signal_flat, sampling_rate=250)

        if len(peaks) >= 2:

            rr_intervals = (
                np.diff(peaks) / 250.0
            )

            mean_rr = np.mean(rr_intervals)

            std_rr = np.std(rr_intervals)

            min_rr = np.min(rr_intervals)

            max_rr = np.max(rr_intervals)

            rr_range = max_rr - min_rr

            if len(rr_intervals) >= 2:

                rmssd = np.sqrt(
                    np.mean(
                        np.diff(rr_intervals) ** 2
                    )
                )

    except Exception:
        pass

    # =====================================
    # Frequency-domain features
    # =====================================

    fft_values = np.abs(
        fft(signal_flat)
    )

    fft_values = fft_values[: len(fft_values) // 2]

    spectral_energy = np.sum(
        fft_values ** 2
    )

    dominant_frequency = np.argmax(
        fft_values
    )

    probabilities = (
        fft_values /
        (np.sum(fft_values) + 1e-10)
    )

    spectral_entropy = -np.sum(
        probabilities *
        np.log2(probabilities + 1e-10)
    )

    return {
        "mean": float(mean),
        "median": float(median),
        "std": float(std),
        "variance": float(variance),
        "min": float(min_value),
        "max": float(max_value),
        "range": float(value_range),
        "rms": float(rms),
        "energy": float(energy),
        "peak_to_peak": float(peak_to_peak),
        "waveform_length": float(waveform_length),

        "mean_rr": float(mean_rr),
        "std_rr": float(std_rr),
        "rmssd": float(rmssd),

        "min_rr": float(min_rr),
        "max_rr": float(max_rr),
        "rr_range": float(rr_range),

        "dominant_frequency": float(dominant_frequency),
        "spectral_energy": float(spectral_energy),
        "spectral_entropy": float(spectral_entropy),
        "skewness": float(signal_skewness),
        "kurtosis": float(signal_kurtosis),
    }