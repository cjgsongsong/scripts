import pikepdf
import sys

file = sys.argv[1]

pikepdf.open(file, password=sys.argv[2], allow_overwriting_input=True) \
       .save(file)
