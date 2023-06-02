# This shell script directly calls the python interpreter
# on the python script that will perform an affine alignment.
# It also passes the four arguments that this script is called with.
# The four arguments will be, in this order, the path (absolute or relative)
# to the sequences file, the path to the matrix file, and the gap open and extension penalty.

python affine.py ${1} ${2} ${3} ${4}
