# This example shell script directly calls the python interpreter
# on a hypothetical python script that will do an affine alignment.
# It also passes the four arguments that this script is called with.
# The four arguments will be, in this order, the path (absolute or relative)
# to the sequences file, the path to the matrix file, and the gap open and extension penalty.
# You'll need to edit this file for the language of your choosing.
# Come to office hours if you need additional clarification.
python affine.py ${1} ${2} ${3} ${4}
