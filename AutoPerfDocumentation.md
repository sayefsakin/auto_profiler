Automated Performance Analysis
----------------------------------------------------

Documentation on how to automate the performance analysis pipeline. As conducting profiling and tracing have [different meanings](https://vampir.eu/tutorial/manual/introduction), throughout this documentation, the term **profiler** is used to indicate performance analysis tool.

This considers the **ExaGO** application and relevant performance analysis tools (like 
nvprof, HPCTookit, etc.) are already pre-installed (possibly using [Spack](https://spack.readthedocs.io/en/latest/features.html)). A sample **Spack** 
configuration file with Exago, [HPCToolkit](http://hpctoolkit.org/), and [TAU](https://hpc.llnl.gov/software/development-environment-software/tau-tuning-and-analysis-utilities) is provided [here](spack.yaml). After doing the necessary installation, simply run the performance analysis script:

```shell
python3 perf_pipeline.py
```

This script takes one command line argument parameter - a TOML file. If no argument is provided, it will read from a default file `sample_testsuite.toml`. 
To run the script with any other TOML file:

```shell
python3 perf_pipeline.py opflow_testsuite.toml
```

## Configuring TOML file
By default, the following keys should be provided in the TOML file:

- `testsuite_name` : Value could be any customized string for naming this testsuite.
- `application` : A string with an ExaGO application name, ex. `opflow` or `scopflow`.
- `mpi_rank` : An integer with the number of mpi ranks
- `iterations`: Number of times each testcase should be run. This is **NOT** hiop or ipopt iterations.

### Providing ExaGO arguments
Also, **ExaGO** arguments which should be same acrosss the testcases should be provided in a hash table titled `[presets]`. No need to add -(dash) before 
each key. For example, defining `-netfile`, `-hiop_verbosity_level`, and  `-print_output` for all testcases can be done as follows,

```yaml
[presets]
netfile = '../datafiles/case_ACTIVSg200.m'
hiop_verbosity_level = 3
print_output = 0
```

Then each testcase should be provided with an array of tables titled `[[testcase]]`. For example, defining two testcases with different solvers can be done 
as follows,
```yaml
[[testcase]]
opflow_solver = 'HIOP'
opflow_model = 'POWER_BALANCE_HIOP'

[[testcase]]
opflow_solver = 'IPOPT'
opflow_model = 'POWER_BALANCE_POLAR'
```

Here, the keys for `presets` and `testcases` are merged into a single dictionary. Therefore, values for duplicate keys in `presets` will get overwritten with 
what is defined in `testcase`. Single ExaGO arguments (without any value) like `log_view` should be provided with key `argument_list` and values as string 
with space separated arguments. Note that, to show execution time reported by PETSc log (for example OPFLOWSolve), using `log_view` will enable collecting 
that value.

To set HIOP and IPOPT parameters, add `hiop_` and `ipopt_` before each key. For example,
```yaml
[[testcase]]
ipopt_print_level = 0
ipopt_max_iter = 100

[[testcase]]
hiop_compute_mode = 'CPU'
hiop_max_iter = 100
```
For the first testcase, it will create `ipopt.opt` file in the current directory and write the follows,
```
print_level = 0
max_iter = 100
```
For the second testcase, it will write to `hiop.options` file without the `hiop_` prefix.

### Providing Performance Analysis Tool
To, execute ExaGO with a performance analysis tool, use an array of tables titled `[[profiler]]`. Here keys should be as follows,

- `tool` : Executable for the performance analysis tool. For example: `nvprof`, `hpcrun`, `tau_exec`, etc.
- `too_args`: Arguments for the profiler. For example, to output nvprof to a log file, use `'--log-file nvprofOutput'`.
- `tool_envs`: Environment variables that is required to export for the profiler. This should be a string with space separated words, where each word 
  being key=value for each environment variable. For example, `'TAU_PROFILE=1 PROFILEDIR=./profiler_dumps'` set the environment variables `TAU_PROIFLE` and 
  `PROFILEDIR`. 

Use blank array table to execute without any profiler. For example, 
```yaml
[[profiler]]

[[profiler]]
tool = 'nvprof'
tool_args = '--log-file nvprofOutput'

[[profiler]]
tool = 'hpcrun'
tool_args = '--disable-auditor -t -o ./profiler_dumps'

[[profiler]]
tool = 'tau_exec'
tool_args = '-io'
tool_envs = 'TAU_PROFILE=1 PROFILEDIR=./profiler_dumps'
```

This will run ExaGO with
- no tool
- nvprof (Nvidia nvprof)
- hpcrun (HPCToolkit)
- tau_exec (TAU)

### What is being executed
This will run **ExaGO** application as a subprocess with each testcase by the defined number of `iterations` with each profiler, as follows:
```shell
mpiexec -n <mpi_rank> <profiler.tool> <profiler.tool_args> <application> <presets> <testcase>
```

### Output Log
The output log is printed directly in the standard output with the prefix `Auto Profiler Log ======> `. Output log can be controlled with the `DEBUG` 
variable which supports 3 values:
- 0: basic, will only print default output like execution time.
- 1: moderate, Additionally prints ExaGO output and error messages, like file not found.
- 2: all, Additionally reports the parsed TOML keys, prepared command line arguments.

In the basic mode it prints the following,

```shell
With <profiler tool name> Total Iterations: <iteration>, CPU Average time: <time> seconds, std: <time standard deviation>
PETSc reported Solve Time: <time> seconds
Total <solver> iterations: <iteration>, Average time per <solver> iterations: <time> seconds
PETSc reported Solve time per iterations: <time>
```