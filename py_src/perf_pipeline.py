#!/usr/bin/env python3
import toml
import sys
import shutil
import os
import time
import re
from subprocess import call, Popen, PIPE

#
# Print Debug levels
# 0: basic
# 1: moderate
# 2: all
DEBUG = 0

def print_debug(level, str):
    if DEBUG>=level:
        print(str)

def do_perf_measure(in_file):
    testsuite = toml.load(in_file)
    params = testsuite['presets'];
    app_name = testsuite['application']

    mpi_cmd = None
    if "mpi_rank" in testsuite:
        mpi_cmd = ["mpiexec", "-n", str(testsuite['mpi_rank'])]

    profiler_cmd_list = [[]]
    my_env = os.environ.copy()
    if "profiler" in testsuite:
        for prof in testsuite['profiler']:
            prof_tool = prof['tool']
            if shutil.which(prof_tool) is None:
                print_debug(0, prof_tool + ' not installed')
            else:
                print_debug(1, prof_tool + ' found')
                pcmd = [prof_tool]
                if 'tool_args' in prof:
                    pcmd.extend(prof['tool_args'].split())
                if profiler_cmd_list is None:
                    profiler_cmd_list = list()
                profiler_cmd_list.append(pcmd)

                if "tool_envs" in prof:
                    t_envs = prof["tool_envs"].split()
                    for env in t_envs:
                        kv = env.split('=')
                        print_debug(2, 'env key: ' + kv[0] + ' env value: ' + kv[1])
                        my_env[kv[0]] = kv[1]
                    print_debug(1, 'profile dir set')
        print_debug(2, profiler_cmd_list)

    if shutil.which(app_name) is None:
        print_debug(0, app_name + ' not installed')
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
            print_debug(2, command)
            print_debug(2, '----')
            #command = ['ls', '-l']
            #call(command)
            
            exago_runs_successfully = False
            suc_str = 'Finalizing ' + app_name + ' application.'

            timeStarted = time.time()
            proc = Popen(command, stdout=PIPE, universal_newlines=True, env=my_env)

            for line in proc.stdout.readlines():
                #print(line, end='')
                if exago_runs_successfully is False and suc_str in line:
                    exago_runs_successfully = True
    
            timeDelta = time.time() - timeStarted
            if exago_runs_successfully:
                print_debug(1, app_name + " runs successfully")
                tool_name = 'no tool'
                if profiler_cmd:
                    tool_name = profiler_cmd[0]
                print_debug(0, "Time measured for " + tool_name + ": " + str(timeDelta) + " seconds.")
            else:
                print_debug(0, app_name + " did NOT run")
            break

if __name__ == '__main__':
    in_file = "sample_testsuite.toml"
    if len(sys.argv) > 1:
        in_file = sys.argv[1]
    else:
        print_debug(0, 'No toml file provided. Using default file: ' + in_file)
    if os.path.exists(in_file):
        do_perf_measure(in_file)
    else:
        print_debug(0, in_file + ' not found')
