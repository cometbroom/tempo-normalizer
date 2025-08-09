import librosa
import argparse
from tempo_normalizer import Change
from pathlib import Path

def detect_tempos(audio_file: str, beats_per_bar: int = 4) -> list[Change]:
    y, sr = librosa.load(audio_file)
    tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
    beat_times = librosa.frames_to_time(beat_frames, sr=sr)

    changes = []
    for start in range(0, len(beat_times), beats_per_bar):
        end = min(start + beats_per_bar, len(beat_times))
        bar_beats = beat_times[start:end]
        if len(bar_beats) < 2:
            # For incomplete bars with less than 2 beats, skip or use previous BPM, but here we skip adding a new change
            break
        bar_duration = bar_beats[-1] - bar_beats[0]
        num_intervals = len(bar_beats) - 1
        avg_ibi = bar_duration / num_intervals
        bpm = 60 / avg_ibi
        changes.append(Change(beat=float(start), bpm=float(bpm)))

    return changes


def main() -> None:
    parser = argparse.ArgumentParser(description="Detect tempo changes per bar in an audio file and output as CSV.")
    parser.add_argument('audio_file', help='input audio file (wav, mp3, etc.)')
    parser.add_argument('-o', help='output CSV file with beat,bpm', type=argparse.FileType('w'), required=False)
    parser.add_argument('--beats_per_bar', type=int, default=4,
                        help='number of beats per bar (time signature assumption)')

    args = parser.parse_args()

    changes = detect_tempos(args.audio_file, args.beats_per_bar)

    csv_content = "\n".join(f"{c.beat},{c.bpm}" for c in changes)
    if hasattr(args, 'output_csv'):
        Path(args.output_csv).write_text(csv_content, encoding="UTF-8")
        print(f"Tempo changes written to {args.output_csv}")
    else:
        print(csv_content)


if __name__ == '__main__':
    main()