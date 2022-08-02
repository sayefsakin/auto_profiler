#!/usr/bin/env python3
import toml
import sys
from subprocess import call, Popen, PIPE

DEBUG = 1

def do_perf_measure():
    testsuite = toml.load("sample_testsuite.toml")
    params = testsuite['presets'];

    for tests in testsuite['testcase']:
        command = list()
        command.append('scopflow')

        params.update(tests)
        for key in params:
            command.append('-'+ key)
            command.append(str(params[key]))
        if DEBUG:
            print(command)
            print('----')
        #command = ['ls', '-l']
        #call(command)
        proc = Popen(command, stdout=PIPE, universal_newlines=True)
        for line in proc.stdout.readlines():
            print(line, end='')
        break

if __name__ == '__main__':
    do_perf_measure()
