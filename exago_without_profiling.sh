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
#export TIMEFORMAT=%3R
#echo "OPFLOW raw" >> $TFILE
#(time opflow -opflow_solver HIOP -hiop_compute_mode GPU \
#	-netfile /nfs/gce/projects/ExaGO/exago_src/exago/datafiles/case9/case9mod.m \
#	-opflow_model PBPOLRAJAHIOP -print_output 0 \
#	-hiop_verbosity_level 0) &>> $TFILE

DIR="${BASH_SOURCE%/*}"
if [[ ! -d "$DIR" ]]; then DIR="$PWD"; fi
. "$DIR/load_vars.sh"

#/usr/bin/time --output=$TFILE --append --format="%e seconds" \
#	$MPI_EXEC $SCOPFLOW_CPU $NO_PRINT
#eval $EX_CMD
first=1
last=3
echo "Without any profiling tool" >> $TFILE
for i in `seq $first $last`
do
	exec 3>&1 4>&2
	time_taken=$(TIMEFORMAT="%3R"; { time $MPI_EXEC $SCOPFLOW_CPU $NO_PRINT 1>&3 2>&4; } 2>&1)
	exec 3>&- 4>&-
	echo "iteration ${i}: ${time_taken}" >> $TFILE
done
