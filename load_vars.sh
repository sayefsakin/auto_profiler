#!/bin/bash
MPI_EXEC="mpiexec -n 1"
NO_PRINT="-hiop_verbosity_level 0 -print_output 0"

OPFLOW_CPU="opflow -opflow_solver IPOPT -hiop_compute_mode cpu \
	-netfile /nfs/gce/projects/ExaGO/exago_src/exago/datafiles/case9/case9mod.m \
	-opflow_model POWER_BALANCE_POLAR"

OPFLOW_GPU="opflow -opflow_solver HIOP -hiop_compute_mode GPU \
	-netfile /nfs/gce/projects/ExaGO/exago_src/exago/datafiles/case9/case9mod.m \
	-opflow_model PBPOLRAJAHIOP"

SCOPFLOW_CPU="scopflow -scopflow_solver EMPAR -hiop_compute_mode CPU \
	-netfile /nfs/gce/projects/ExaGO/exago_src/exago/datafiles/case9/case9mod.m \
	-ctgcfile /nfs/gce/projects/ExaGO/exago_src/exago/datafiles/case9/case9.cont \
	-scopflow_mode 1 \
	-scopflow_subproblem_model POWER_BALANCE_POLAR \
	-scopflow_subproblem_solver IPOPT \
	-scopflow_Nc 3"

SCOPFLOW_GPU="scopflow -scopflow_solver HIOP -hiop_compute_mode GPU \
	-netfile /nfs/gce/projects/ExaGO/exago_src/exago/datafiles/case9/case9mod.m \
	-ctgcfile /nfs/gce/projects/ExaGO/exago_src/exago/datafiles/case9/case9.cont \
	-scopflow_mode 1 \
	-scopflow_subproblem_model PBPOLRAJAHIOP \
	-scopflow_subproblem_solver HIOP \
	-scopflow_Nc 3"
