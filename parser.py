from music21 import note, converter, meter, stream, tie, analysis
import numpy as np
import pandas as pd
import glob


def parse_dataset(folder, filetype='krn', voice=0, key=False, metrical_depth=False):
    """Parses all score files of a given type within a folder.

    Args:
        folder: the directory containing the dataset
        filetype: type of the digital music scores
        voice: soprano is typically the first in **kern files, so the last part (i.e. voice=-1)
        metrical_depth: whether to compute the metrical depth of each note event
        key: whether to compute the key, based on the current and all past notes in the song

    Returns:
        a list of dataframes that represent each song
    """
    file_list = glob.glob(folder + '/*.' + filetype)

    song_list = []
    for name in file_list:
        song_list += [parse_song(name, voice=voice, key=key,
                                 metrical_depth=metrical_depth)]

    return song_list


def parse_song(filepath, voice=0, key=False, metrical_depth=False):
    """Parses a file using music21.

    Supported formats are xml, krn, abc, mid, ...

    Args:
        filepath: the path to the score file

    Returns:
        dataframe of song as multi-dimensional time series
    """
    try:
        song = converter.parse(filepath)
    except converter.ConverterException:
        raise ValueError('Song {} could not be parsed!'.format(filepath))

    song_voice = song.parts[voice]

    ts_pitch, ts_duration, ts_pos_in_bar, ts_tie_flag = parse_measures(song_voice)
    assert len(ts_pitch) == len(ts_duration) == len(ts_pos_in_bar) == len(ts_tie_flag)

    df = pd.DataFrame({'pitch': np.array(ts_pitch, dtype=np.int8),
                       'duration': np.array(ts_duration, dtype=np.float16),
                       'pos_in_bar': np.array(ts_pos_in_bar, dtype=np.float16),
                       'tie_flag': np.array(ts_tie_flag, dtype=np.bool),
                       })

    if key:
        ts_tonic, ts_mode = compute_tonic_and_mode(ts_pitch)
        assert len(ts_pitch) == len(ts_tonic) == len(ts_mode)
        df = df.join(pd.DataFrame({'mode': ts_mode,
                                   'tonic': np.array(ts_tonic, dtype=np.int8)
                                   }))

    if metrical_depth:
        ts_md = compute_metrical_depth(song_voice)
        assert len(ts_pitch) == len(ts_md)
        df = df.join(pd.DataFrame({'metrical_depth': np.array(ts_md, dtype=np.int8)}))

    return df


def parse_measures(voice: stream.Stream):
    """Parses the basic viewpoints pitch, duration, position in bar and marks ties.

    Duration and position in bar are given in quarter lengths (float). Rests are pitch 0.

    Args:
        voice: a part of the possibly multidimensional (e.g. in chorales) stream

    Return:
        tuple of parsed lists for each viewpoint
    """
    ts_pitch = []
    ts_duration = []
    ts_pos_in_bar = []
    ts_tie_flag = []

    # fill time series with score data
    for measure in voice:
        # flag reset every measure
        if hasattr(measure, '__iter__'):
            for event in measure:
                if isinstance(event, note.Note):
                    ts_pitch += [event.pitch.midi]
                    ts_duration += [event.duration.quarterLength]
                    ts_pos_in_bar += [event.offset]

                    if event.tie == tie.Tie("start"):
                        ts_tie_flag += [True]
                    else:
                        ts_tie_flag += [False]

                if isinstance(event, note.Rest):
                    ts_pitch += [0]
                    ts_duration += [event.duration.quarterLength]
                    ts_pos_in_bar += [event.offset]
                    ts_tie_flag += [False]

    return ts_pitch, ts_duration, ts_pos_in_bar, ts_tie_flag


def compute_metrical_depth(voice: stream.Stream):
    try:
        # annotate the voice
        analysis.metrical.labelBeatDepth(voice)
    except meter.MeterException:
        print('WARNING: Could not compute metrical depth!')

    ts_metrical_depth = []
    for measure in voice:
        if hasattr(measure, '__iter__'):
            for event in measure:
                if isinstance(event, note.Note) or isinstance(event, note.Rest):
                    ts_metrical_depth += [len(event.lyrics)]

    return ts_metrical_depth


def compute_tonic_and_mode(ts_pitch):
    ts_tonic = []
    ts_mode = []
    for idx in range(len(ts_pitch)):
        tonic_, mode_ = compute_key(ts_pitch[0:idx + 1], np.ones(idx + 1))
        ts_tonic += [tonic_]
        ts_mode += [mode_]
    return ts_tonic, ts_mode


def compute_key(ts_pitch, ts_duration, method='key.temperley'):
    stream_ = convert_to_stream(ts_pitch, ts_duration)
    res = stream_.analyze(method)
    tonic_ = res.tonic.midi
    mode_ = res.mode
    return tonic_, mode_


def convert_to_stream(ts_pitch, ts_duration):
    notes = stream.Stream()
    for pitch, duration in zip(list(ts_pitch), list(ts_duration)):
        n = note.Note(pitch, quarterLength=duration)
        notes.append(n)
    return notes
