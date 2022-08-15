#!/usr/bin/env python3
import toml
import sys
import shutil
import os
import io
import time
import re
import math
import copy
from subprocess import call, Popen, PIPE

#
# Print Debug levels
# 0: basic
# 1: moderate
# 2: all
DEBUG = 0

def print_debug(level, str):
    if DEBUG>=level:
        print('Auto Profiler Log ======> ', end='')
        print(str)

def update_hiop_options(options, app):
    hiops = dict()
    delList = list()
    app_prefix = ''
    op_file_name = ''
    st_ind = 1
    if options[app + '_solver'] == 'HIOP' or options[app + '_solver'] == 'HIOPSPARSE':
        app_prefix = 'hiop_'
        op_file_name = 'hiop.options'
        st_ind = 5
    elif options[app + '_solver'] == 'IPOPT':
        app_prefix = 'ipopt_'
        op_file_name = 'ipopt.opt'
        st_ind = 6
    
    if st_ind == 1:
        hiops['max_iter'] = 1
    else:
        for key in options:
            if key.startswith(app_prefix):
                hiop_key = key[st_ind:]
                hiop_value = options[key]
                hiops[hiop_key] = hiop_value
                delList.append(key)
        with open(op_file_name, 'w') as hof:
            for key in hiops:
                hof_str = key + ' ' + str(hiops[key])
                hof.write(hof_str + '\n')
        for dl in delList:
            options.pop(dl, None)
    return hiops


def do_perf_measure(in_file):
    testsuite = toml.load(in_file)
    if 'application' not in testsuite:
        print_debug(0, "Please provide application")
    if 'presets' not in testsuite:
        print_debug(0, "Please provide presets")

    app_name = testsuite['application']
    preset_params = testsuite['presets'];
    iterations = 1
    if 'iterations' in testsuite:
        iterations = testsuite['iterations']

    mpi_cmd = None
    if "mpi_rank" in testsuite:
        mpi_cmd = ["mpiexec", "-n", str(testsuite['mpi_rank'])]

    profiler_cmd_list = list()
    my_env = os.environ.copy()
    if "profiler" in testsuite:
        for prof in testsuite['profiler']:
            if 'tool' not in prof:
                prof_tool = 'no tool'
                profiler_cmd_list.append([])
                continue
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
    
    test_number = 1
    for tests in testsuite['testcase']:
        print_debug(0, "For testcase " + str(test_number))
        test_number = test_number + 1
        for profiler_cmd in profiler_cmd_list:
            command = list()
            #command.append("time")
            if mpi_cmd is not None:
                command.extend(mpi_cmd)
            
            tool_name = 'no tool'
            if profiler_cmd:
                tool_name = profiler_cmd[0]
                command.extend(profiler_cmd)
            
            command.append(app_name)
            params = dict()
            params = copy.deepcopy(preset_params)
            params.update(tests)
            hiop_options = update_hiop_options(params, app_name)
            
            for key in params:
                command.append('-'+ key)
                command.append(str(params[key]))
            print_debug(2, command)
            print_debug(2, '----')
            #command = ['ls', '-l']
            #call(command)
            
            exago_runs_successfully = False
            suc_str = 'Finalizing ' + app_name + ' application.'
            ON_POSIX = 'posix' in sys.builtin_module_names

            # create a pipe to get data
            input_fd, output_fd = os.pipe()

            time_lists = list()
            for i in range(iterations):
                timeStarted = time.time()
                #proc = Popen(command, stdout=PIPE, universal_newlines=True, bufsize=1, env=my_env)
                proc = Popen(command, stdout=output_fd, universal_newlines=True, bufsize=1, env=my_env, close_fds=ON_POSIX)
                os.close(output_fd)
                with io.open(input_fd, 'r', buffering=1) as ff:
                    for line in ff:
                        print(line, end='')
                        if exago_runs_successfully is False and suc_str in line:
                            exago_runs_successfully = True

                #for line in proc.stdout.readlines():
                #    print(line, end='')
                #    if exago_runs_successfully is False and suc_str in line:
                #        exago_runs_successfully = True
    
                timeDelta = time.time() - timeStarted
                if exago_runs_successfully:
                    print_debug(1, app_name + " runs successfully")
                    time_lists.append(timeDelta)
                    print_debug(2, "Total measured time with " + tool_name + ": " + str(round(timeDelta,5)) + " seconds.")
                else:
                    print_debug(0, app_name + " did NOT run with " + tool_name)
            avg_tm = sum(time_lists) / len(time_lists)
            var  = sum(pow(x-avg_tm,2) for x in time_lists) / len(time_lists)
            avg_tm_str = str(round(avg_tm,5))
            avg_std = str(round(math.sqrt(var),5))
            print_debug(0, "With " + tool_name + " Total Iterations: " + str(len(time_lists)) + ", Average time: " + avg_tm_str + " seconds, std: " + avg_std)
            if 'max_iter' in hiop_options:
                hiop_avg_time = str(round(avg_tm / hiop_options['max_iter'],5))
                solver_name = params[app_name + '_solver']
                print_debug(0, "Total " + solver_name + " iterations: " + str(hiop_options['max_iter']) + ", Average time per " + solver_name + " iterations: " + hiop_avg_time + " seconds")

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
