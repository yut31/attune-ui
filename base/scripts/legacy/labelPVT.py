from nova2026.data import eeg
from nova2026.config import DATA_DIR
from pathlib import Path
import numpy as np
import torch

from nova2026.data.channels import EEG_CHANNELS


ROOT = DATA_DIR / "COG-BCI"
SAMPLE_RATE = 128  # Hz
# SAMPLE_LENGTH = 2400  # ms
SAMPLE_LENGTH = 2000  # ms
WINDOW_LENGTH = 2000  # ms
# STEP_SIZE = 300  # ms


TRANSLATION = {
    "10": "PVT Start",
    "11": "PVT Trial/ISI Start",
    "12": "PVT ISI Error",
    "13": "PVT Stimulus",
    "14": "PVT Response",
    "15": "PVT  End",
    "boundary": "Boundary",
}


def load_subjects():
    subs = []
    for sub in ROOT.iterdir():
        if "sub" in sub.name and sub.is_dir():
            subs.append(sub.name)
    return np.array(subs)


def load_sessions(sub):
    return np.array([s.name for s in (ROOT / sub).iterdir() if s.is_dir()])


def load_runs(sub, ses):
    return eeg.load(ROOT / sub / ses / "eeg/PVT.set")


def get_trials(raw):
    trials = []
    stmls_tmstp = 0
    rsp_tmstp = 0
    err_tmstp = 0
    for ann in raw.annotations:
        # Evil fix for the onset
        tmstp = np.int32(ann["onset"] * 1000)
        if ann["description"] == "13":  # stimulus
            stmls_tmstp = tmstp
        elif ann["description"] == "14":  # response
            trials.append(
                np.array(
                    [
                        (tmstp - stmls_tmstp),
                        min(stmls_tmstp - rsp_tmstp, stmls_tmstp - err_tmstp),
                        stmls_tmstp,
                        tmstp,
                    ]
                )
            )
            rsp_tmstp = tmstp
        elif ann["description"] == "12":  # error
            trials.append(np.array([-1, -1, -1, tmstp]))
            err_tmstp = tmstp
    return np.asarray(trials).reshape(-1, 4)


def load_eeg_trials(data_list, label_list, meta_list, raw, trials, sub, ses, label):
    for trial in trials:
        stmls_time = trial[2]
        batch = []
        tmax = (stmls_time - 100) / 1000
        idxmax = raw.time_as_index(tmax)[0]
        idxmin = idxmax - int(WINDOW_LENGTH / 1000 * SAMPLE_RATE)
        if idxmin < 0 or idxmax > raw.n_times:
            continue
        batch.append(raw.get_data(picks=EEG_CHANNELS, start=idxmin, stop=idxmax) * 1e6)
        data_list.append(np.stack(batch, axis=0))
        meta_list.append((sub, ses, trial[0]))
        label_list.append(label)


def split_by_reaction_time(trials):
    """Return slowest 10% and remainder; skip sessions too small for two classes."""
    trials = trials[np.argsort(trials[:, 0])]
    n = len(trials) // 10
    if n == 0:
        return trials[:0], trials[:0]
    return trials[-n:], trials[:-n]


def label_data():
    data_list = []
    label_list = []
    meta_list = []

    subs = load_subjects()
    for sub in subs:
        sessions = load_sessions(sub)
        for ses in sessions:
            raw = load_runs(sub, ses)
            trials = get_trials(raw)
            raw.load_data()
            # Filter 0.5Hz - 45Hz
            raw.filter(0.5, 45.0, fir_design="firwin", verbose=False)
            raw.resample(SAMPLE_RATE)

            raw.pick(EEG_CHANNELS)

            qualified_mask = trials[:, 1] > SAMPLE_LENGTH + 200  # 200ms as buffer

            cleaned_trials = trials[qualified_mask]
            bottom_10_percent, other = split_by_reaction_time(cleaned_trials)

            load_eeg_trials(
                data_list, label_list, meta_list, raw, bottom_10_percent, sub, ses, 1
            )

            load_eeg_trials(data_list, label_list, meta_list, raw, other, sub, ses, 0)

    if not data_list:
        raise ValueError("No usable trials; check dataset paths and session lengths")
    data_array = np.array(data_list)
    label_array = np.array(label_list)
    meta_array = np.array(meta_list)

    print(data_array.shape, label_array.shape, meta_array.shape)

    data_tensor = torch.from_numpy(data_array).float()
    label_tensor = torch.from_numpy(label_array).long()

    torch.save(
        {
            "data": data_tensor,
            "labels": label_tensor,
            "metadata": meta_array,
        },
        ROOT / "PVT_data_2000ms_200ms.pt",
    )


if __name__ == "__main__":
    label_data()
