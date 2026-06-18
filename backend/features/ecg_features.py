import numpy as np
import neurokit2 as nk

from scipy.stats import skew
from scipy.stats import kurtosis
from scipy.fft import fft


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

        _, info = nk.ecg_peaks(
            signal_flat,
            sampling_rate=250
        )

        peaks = info["ECG_R_Peaks"]

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