# TEMPO NORMALIZER

Converts any song in a non-constant tempo into a constant-tempo song. Only supports songs with snap BPM changes (BPMs
that change instantly). You might notice that this script was created with very specific purposes.

You need:

- Audio you want to process (wav only)
- CSV of BPM changes

CSV must be in this format:

```
beat_no,new_bpm
```

Where there is at least one row, and the `beat_no` for the first row must be a 0. There are **no headers** in the CSV.
Example:

```
0,120
4,150
8,180
```

Represents a song that starts with a BPM of 120, changes to 150 at beat 4, and changes to 180 at beat 8. **Beats count
from 0.** This csv should describe the tempo of the input audio file.

## The script

Does exactly what it is told to. Requires all packages in `requirements.txt`, works with Python 3.9 or later.

```
usage: tempo_normalizer.py [-h] audio_file csv_file out_bpm out_file

A script with 3 positional arguments.

positional arguments:
  audio_file  input audio file, wav only
  csv_file    csv file, specs in README
  out_bpm     output wav will have this bpm
  out_file    wav only, save to

options:
  -h, --help  show this help message and exit
```
