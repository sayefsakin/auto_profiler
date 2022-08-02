#!/bin/bash
TFILE=time_lists.txt
TDASH="=========================="
if [ $# -eq 1 ]
then
	TFILE=$1
fi
rm -f $TFILE

if ! [ -x "$(command -v scopflow)" ]; then
	echo 'Error: Exago is not installed.' >&2
	exit 1
fi
if ! [ -x "$(command -v nsys)" ]; then
	echo 'Error: NVIDIA Nsight is not installed.' >&2
	exit 1
fi

DIR="${BASH_SOURCE%/*}"
if [[ ! -d "$DIR" ]]; then DIR="$PWD"; fi
. "$DIR/load_vars.sh"

NSYS="nsys profile"

first=1
last=3
echo "With NSight" >> $TFILE
for i in `seq $first $last`
do
	rm -f *.nsys-rep
	exec 3>&1 4>&2
	time_taken=$(TIMEFORMAT="%3R"; { time $MPI_EXEC $NSYS $SCOPFLOW_CPU $NO_PRINT 1>&3 2>&4; } 2>&1)
	exec 3>&- 4>&-
	echo "iteration ${i}: ${time_taken}" >> $TFILE
done
