
from pathlib import Path
from librosa.core import resample
from soundfile import write
from librosa import load

DESIRED_SAMPLE_RATE = 44100

def ensure_sample_rate(original_sample_rate, waveform, desired_sample_rate=DESIRED_SAMPLE_RATE):
    """Resample waveform if required."""
    if original_sample_rate != desired_sample_rate:
        waveform = resample(waveform, orig_sr=original_sample_rate, target_sr=desired_sample_rate)
    return waveform


def extract_waveform(wav_file_path: Path, sample_rate=DESIRED_SAMPLE_RATE):
    path = wav_file_path.absolute().as_posix()

    wav_data, sr = load(path)
    wav_data = ensure_sample_rate(sample_rate, wav_data)
    return wav_data


def save_audio_mono(wav_array, sr, path):
    write(Path(path), data=wav_array, samplerate=sr, format='wav')
    return path
