# Score Parser

A small library to parse digital music scores into pandas dataframes using music21.

## Usage

To parse all songs of a given type within the specified folder import `parser.py` and run:

`parse_dataset(folder, filetype='krn', voice=0, key=False, metrical_depth=False)`

Any filetype supported by music21 (which is basically any) can be specified. Additionally, the output can be augmented by the musical viewpoints key and metrical depth.

## Parsing the Pearce Corpus

The script `pearce_corpus.py` parses the well established benchmarking corpus published by Pearce: http://webprojects.eecs.qmul.ac.uk/marcusp/software/JNMR2004.zip

Follow the instructions in the script to set the corpus as well as cross-validation filepaths, then run. The parsed corpus will be stored as pickles in the path of the corpus.

Enjoy!
