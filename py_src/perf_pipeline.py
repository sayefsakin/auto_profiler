#!/usr/bin/env python3
import toml
import sys
import shutil
import os.path
import time
from subprocess import call, Popen, PIPE

DEBUG = 1

def do_perf_measure(in_file):
    testsuite = toml.load(in_file)
    params = testsuite['presets'];
    app_name = testsuite['application']

    mpi_cmd = None
    if "mpi_rank" in testsuite:
        mpi_cmd = ["mpiexec", "-n", str(testsuite['mpi_rank'])]

    profiler_cmd_list = [[]]
    if "profiler" in testsuite:
        for prof in testsuite['profiler']:
            prof_tool = prof['tools']
            if shutil.which(prof_tool) is None:
                print(prof_tool + ' not installed')
            else:
                print(prof_tool + ' found')
                pcmd = [prof_tool]
                pcmd.extend(prof['tool_args'].split())
                if profiler_cmd_list is None:
                    profiler_cmd_list = list()
                profiler_cmd_list.append(pcmd)
        print(profiler_cmd_list)

    if shutil.which(app_name) is None:
        print(app_name + ' not installed')
        return
    
    for profiler_cmd in profiler_cmd_list:
        for tests in testsuite['testcase']:
            command = list()
            #command.append("time")
            if mpi_cmd is not None:
                command.extend(mpi_cmd)
            
            if profiler_cmd:
                command.extend(profiler_cmd)
            
            command.append(app_name)

            params.update(tests)
            for key in params:
                command.append('-'+ key)
                command.append(str(params[key]))
            if DEBUG:
                print(command)
                print('----')
            #command = ['ls', '-l']
            #call(command)
            
            #exago_runs_successfully = False
            #suc_str = 'Finalizing ' + app_name + ' application.'

            #timeStarted = time.time()
            #proc = Popen(command, stdout=PIPE, universal_newlines=True)
            #for line in proc.stdout.readlines():
            #    #print(line, end='')
            #    if exago_runs_successfully is False and suc_str in line:
            #        exago_runs_successfully = True
            #
            #timeDelta = time.time() - timeStarted
            #if exago_runs_successfully:
            #    print(app_name + " runs successfully")
            #    print("Time measured from python " + str(timeDelta) + " seconds.")
            #else:
            #    print(app_name + " did NOT run")
            #break

if __name__ == '__main__':
    in_file = "sample_testsuite.toml"
    if len(sys.argv) > 1:
        in_file = sys.argv[1]
    else:
        print('No toml file provided. Using default file: ' + in_file)
    if os.path.exists(in_file):
        do_perf_measure(in_file)
    else:
        print(in_file + ' not found')
