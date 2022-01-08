import pickle
import pyparsing
import numpy as np
from score_parser import parse_dataset

# This script parses the Pearce dataset:
# http://webprojects.eecs.qmul.ac.uk/marcusp/software/JNMR2004.zip
#
# 1. copy the resampling sets into the respective dataset folder and rename each to folds.txt
# 2. update rootpath variable, match folder names with dataset names
# 3. set the remaining parameters
# 4. run

# ## parameters

ROOTPATH = '../xyz'
DATASET_NAMES = ['canadian', 'chorales', 'alsatian', 'yugoslavian', 'swiss', 'austrian', 'german',
                 'chinese']
CV_FOLDS = 'folds.txt'
PARSE_FOLDS = True
COMPUTE_KEYS = False
COMPUTE_METRICAL_DEPTH = False


# ##


def parse_cv_folds(filepath):
    """Parses the CV folds for a dataset.

    Format according to Pearce's resampling set format as used by IDyOM.
    (((TEST (15 11 ...)) (TRAIN (0 1 ...))), ((TEST (12 27 ...)) (TRAIN (0 1 ...))), ... )

    Args:
        filepath:

    Returns:
        list of folds where each fold is a (train indices, test indices) pair
    """
    with open(filepath) as f:
        folds_string = f.readlines()  # 1 line

    parens = pyparsing.nestedExpr('(', ')', content=pyparsing.Word(pyparsing.alphanums))
    folds = parens.parseString(folds_string[0]).asList()[0]
    fold_list = []

    for fold in folds:
        test_indices = fold[0]
        train_indices = fold[1]

        assert train_indices[0] == 'TRAIN' and test_indices[0] == 'TEST'

        fold_list += [(np.array(train_indices[1], dtype=int),
                       np.array(test_indices[1], dtype=int))]

    return fold_list


def pickle_that(data, filename):
    output = open(filename, 'wb')
    pickle.dump(data, output)
    output.close()


def unpickle(filename):
    file = open(filename, 'rb')
    return pickle.load(file)


def load_corpus(path):
    """Loads the pickled datasets."""
    datasets = []
    for name in DATASET_NAMES:
        datasets += [unpickle(path + '/' + name + '.pkl')]

    return datasets


def save_corpus(path, folds=True, key=True, metrical_depth=True):
    """Saves the datasets.

    Each dataset is pickled as a list of dataframe, or if folds are parsed to as a pair of the
    dataframes and CV folds.
    """
    for name in DATASET_NAMES:
        folder = path + '/' + name + '/'
        voice = -1  # for 1 parts this is the single part, for 4 parts this is the last
        dataset = parse_dataset(folder, voice=voice, key=key, metrical_depth=metrical_depth)
        data = dataset
        if folds:
            data = (data, parse_cv_folds(folder + CV_FOLDS))
        pickle_that(data, path + '/' + name + '.pkl')


if __name__ == '__main__':
    save_corpus(ROOTPATH, folds=PARSE_FOLDS, key=COMPUTE_KEYS,
                metrical_depth=COMPUTE_METRICAL_DEPTH)
