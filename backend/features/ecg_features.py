import numpy as np
from scipy.fft import fft


def extract_features(signal):
    """
    Extract statistical and frequency-domain features from ECG signal.
    """

    signal_flat = signal.flatten()

    # Statistical features

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

    # Frequency-domain features

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
        "signal_length": int(signal_length),
        "waveform_length": float(waveform_length),
        "dominant_frequency": float(dominant_frequency),
        "spectral_energy": float(spectral_energy),
        "spectral_entropy": float(spectral_entropy),
    }