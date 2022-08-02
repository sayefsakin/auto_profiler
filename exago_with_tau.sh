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
if ! [ -x "$(command -v tau_exec)" ]; then
	echo 'Error: TAU is not installed.' >&2
	exit 1
fi

DIR="${BASH_SOURCE%/*}"
if [[ ! -d "$DIR" ]]; then DIR="$PWD"; fi
. "$DIR/load_vars.sh"

export TAU_PROFILE=1
export PROFILEDIR=/nfs/gce/projects/ExaGO/tau_opflow_profiles
export TAU_TRACE=0
export TRACEDIR=/nfs/gce/projects/ExaGO/tau_opflow_traces
TAU_RUN="tau_exec -io"

first=1
last=1
echo "With TAU" >> $TFILE
for i in `seq $first $last`
do
	exec 3>&1 4>&2
	time_taken=$(TIMEFORMAT="%3R"; { time $MPI_EXEC $TAU_RUN $OPFLOW_CPU $NO_PRINT 1>&3 2>&4; } 2>&1)
	exec 3>&- 4>&-
	echo "iteration ${i}: ${time_taken}" >> $TFILE
done
