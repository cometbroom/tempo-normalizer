import argparse
from dataclasses import dataclass
from pathlib import Path

import librosa
import numpy as np
from pydub import AudioSegment
from itertools import zip_longest


@dataclass
class Change:
    """beat - at this beat, counting from 0, the tempo changes to bpm
    """
    beat: float
    bpm: float

    @classmethod
    def from_list(cls, inputs: list[tuple[float, float]]) -> list["Change"]:
        return [cls(a, b) for a, b in inputs]


def stretch_audio(audio: AudioSegment, speed_up_factor: float) -> AudioSegment:
    frame_rate = audio.frame_rate
    samples = np.array(audio.get_array_of_samples(), dtype=np.float32)
    samples = np.clip(samples / (2 ** 15), -1.0, 1.0)
    if audio.channels == 2:
        samples = samples[::2]  # Take every other sample to make it mono
    stretched_samples = librosa.effects.time_stretch(samples, rate=speed_up_factor)
    stretched_samples_int = (stretched_samples * 32767).astype(np.int16)
    stretched_bytes = stretched_samples_int.tobytes()
    output_audio = AudioSegment(
        stretched_bytes,
        frame_rate=frame_rate,
        sample_width=2,
        channels=1
    )
    return output_audio

    # factors = factor_small_number(speed_up_factor)
    # for f in factors:
    #     audio = stretch_audio_ffmpeg_unsafe(audio, f)
    # return audio


@dataclass
class ChangeCandidates:
    seg: AudioSegment
    bpm_from: float
    bpm_to: float

    def apply_speed(self) -> AudioSegment:
        # print(len(self.seg))
        if self.bpm_from < 0.001:
            raise ValueError("BPM from is absurdly close to a division by zero")
        if self.bpm_from == self.bpm_to:
            return self.seg
        stretched = stretch_audio(self.seg, self.bpm_to / self.bpm_from)
        # print(f"COMP: {len(stretched)}, {len(self.seg) * (self.bpm_from / self.bpm_to)}")
        return stretched


def make_constant(base_audio: AudioSegment, bpm_changes: list[Change], output_bpm: float) -> AudioSegment:
    """Make the audio a constant BPM and return it.

    :param base_audio: the base audio to start with, the music should begin right at the start

    :param bpm_changes: a list of BPM changes. they MUST be sorted. The first BPM change must occur at time 0 or this method will error. This list must be sorted by the time the changes occur or this method will error.

    :param output_bpm: BPM for the returned audiosegment instance

    :return: base_audio with its bpm constant if all other arguments meet the description
    """
    base_audio = base_audio.set_channels(1)
    change_list: list[ChangeCandidates] = []
    base_milliseconds = 0.0
    if len(bpm_changes) == 0:
        raise ValueError("BPM change list cannot be empty")
    if bpm_changes[0].beat != 0:
        raise ValueError("First beat must be 0")
    previous_beat = 0
    for current, following in zip_longest(bpm_changes, bpm_changes[1:], fillvalue=None):
        if previous_beat > current.beat:
            raise ValueError("BPM changes must be sorted by the time they occur")
        segment_from = current.beat
        segment_to = following.beat if following is not None else len(base_audio)
        # (segment beat count) * (seconds per beat) * 1000
        segment_length_ms = (segment_to - segment_from) * (60 / current.bpm) * 1000
        change_list.append(ChangeCandidates(
            seg=base_audio[base_milliseconds:base_milliseconds + segment_length_ms],
            bpm_from=current.bpm,
            bpm_to=output_bpm
        ))
        previous_beat = current.beat
        base_milliseconds += segment_length_ms

    fixed_audio = []
    for i, t in enumerate(change_list):
        print(f"Processing {i}/{len(change_list)}")
        fixed_audio.append(t.apply_speed())

    combined = AudioSegment.empty()
    for sample_fixed in fixed_audio:
        combined += sample_fixed
    return combined


def recipe(audio_file: str, csv_file: str, bpm: float, audio_output: str) -> None:
    audio_segment = AudioSegment.from_file(audio_file, format="wav")
    stretched = make_constant(audio_segment,
                              Change.from_list([(tuple([float((a).strip()) for a in t.split(",")])) for t in
                                                Path(csv_file).read_text(encoding="UTF-8").strip().split("\n")]),
                              bpm)
    stretched.export(audio_output, "wav")


def main() -> None:
    parser = argparse.ArgumentParser(description="Makes the tempo of any song with varying tempo constant.")

    parser.add_argument('audio_file', help='input audio file, wav only')
    parser.add_argument('csv_file', help='csv file, specs in README')
    parser.add_argument('out_bpm', type=float, help='output wav will have this bpm')
    parser.add_argument('out_file', help='wav only, save to')
    # Parse the arguments
    args = parser.parse_args()
    recipe(args.audio_file, args.csv_file, args.out_bpm, args.out_file)


if __name__ == '__main__':
    main()
