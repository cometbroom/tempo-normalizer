import subprocess
from io import BytesIO
from pathlib import Path
from librosa.core import load
from soundfile import write


# Function to convert M4A to PCM WAV 16-bit using ffmpeg
def convert_to_wav(sound_file: Path, sr=44100):
    # ffmpeg command to convert M4A to PCM WAV (16-bit). ac means 1 channel, mono
    command = [
        'ffmpeg', '-i', sound_file.absolute().as_posix(), '-f', 'wav', '-ac', '1', '-ar', str(sr),
        '-acodec', 'pcm_s16le', 'pipe:'
    ]

    # Run ffmpeg and capture output
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    wav_data, _ = process.communicate()

    # Read WAV data into numpy array
    wav_io = BytesIO(wav_data)
    wav_array, sample_rate = load(wav_io)

    return wav_array, sample_rate


# Function to convert M4A to PCM WAV 16-bit using ffmpeg
def convert_to_wav_data(audio_data, sr=44100):
    temp_file = Path("./temp.wav")

    if temp_file.exists():
        temp_file.unlink()
    write(temp_file, audio_data, sr)
    # ffmpeg command to convert M4A to PCM WAV (16-bit). ac means 1 channel, mono
    command = [
        'ffmpeg', '-i', temp_file.absolute().as_posix(), '-f', 'wav', '-ac', '1', '-ar', str(sr),
        '-acodec', 'pcm_s16le', 'pipe:'
    ]

    # Run ffmpeg and capture output
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    wav_data, _ = process.communicate()

    # Read WAV data into numpy array
    wav_io = BytesIO(wav_data)
    wav_array, sample_rate = load(wav_io)

    temp_file.unlink()
    return wav_array, sample_rate
