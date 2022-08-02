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
if ! [ -x "$(command -v hpcrun)" ]; then
	echo 'Error: HPCToolkit is not installed.' >&2
	exit 1
fi

DIR="${BASH_SOURCE%/*}"
if [[ ! -d "$DIR" ]]; then DIR="$PWD"; fi
. "$DIR/load_vars.sh"

HPC_RUN="hpcrun --disable-auditor -t"

first=1
last=10
echo "With HPCToolkit" >> $TFILE
for i in `seq $first $last`
do
	exec 3>&1 4>&2
	time_taken=$(TIMEFORMAT="%3R"; { time $MPI_EXEC $HPC_RUN $SCOPFLOW_CPU $NO_PRINT 1>&3 2>&4; } 2>&1)
	exec 3>&- 4>&-
	echo "iteration ${i}: ${time_taken}" >> $TFILE
done
