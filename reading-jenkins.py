import argparse

from pandas._typing import FilePath

# Initialize parser
parser = argparse.ArgumentParser()
parser.parse_args(FilePath)
args = parser.parse_args()
print('Printing Arguments')
print(args)