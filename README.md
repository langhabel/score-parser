# Score Parser

A small library to parse digital music scores into pandas dataframes using music21.

## Installation

Install the Python dependencies (preferably in a venv) using:

```
pip install -r requirements.txt
```

## Usage

To parse all songs of a given type within the specified folder import `parser.py` and run:

```
from score_parser import parse_dataset

parse_dataset(folder, filetype='krn', voice=0, key=False, metrical_depth=False)
````

Any filetype supported by music21 (which is basically any) can be specified. Additionally, the output can be augmented by the musical viewpoints key and metrical depth.

## Example: Parsing the Pearce Corpus

The script `examples/pearce_corpus.py` parses the well established benchmarking corpus published by Pearce: http://webprojects.eecs.qmul.ac.uk/marcusp/software/JNMR2004.zip

Follow the instructions in the script to configure the corpus as well as cross-validation filepaths, then run. The results will be stored as pickles in the directory of the corpus.

Enjoy!
