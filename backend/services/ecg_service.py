import wfdb


def load_ecg(record_path):
    record = wfdb.rdrecord(str(record_path))
    return record.p_signal