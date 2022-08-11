11 Aug 2022
===========================================================

Sayef introduced.

asked what he did

gpu profiling, 
used nvprof, also used TAU
Used TAU for gathering MPI calls

previously used HPCToolkit.


would be nice to reprot the first 5 or 
what fraction of time is being spent in each function

comparative analysis between the version
time per iteration is an important criteria


running on multiple ranks,
if the number of process is huge, 
vampire doesn't support more than 1000 processes for visualization

it will be challanging with mulitple process, HIOP, 120 GPU nodes, 
nvprof or multi 
if you want to show which gpu performing, that is tricky, single node single gpu is well develped
but for multi-gpu it is challenging

you can show how this gpu is performing, across multiple node is tricky
you want to compare this function works in that gpu, to make sure the work is well balanaced
and the communicaction time is affecting.

for AMD gpu
it can proflie if the whole execution is complete, whenever the application exit (nvprof gives partial results)
but 
if the application runs for more than 2hours, it fails for AMD machine (rocprof cant do it)
he used rocprof AMD

reduce the number of iterations is to reduce the number of iterations.
for flop count, rocprof doesn't support fully support it.

How much Memory this application is used on the GPU.
the memory being a bottleneck.

nvidia-smi, can roughly show the gpu (he run it paralley to get the data)


---------------------

with ExaGO he has done flop based counting, which function is taking most floating point operations
and then figuring out the top 10 funcction in terms of flop count in terms of memory used,

then I used roofline based analysis, 
then MPI tau based profilng, he showed MPI overhead and communication cost
we have developed the script, it can get large number of MPI script
We have done multi-node multi-gpu profling using rocprof and also using nvprof
it will generate 6 different profling file for multi-node

he mostly focused on GPU timing and MPI timing

-----

developer devleop their code and periodiccally 

provided feedback which funcctions are provided most of the applications
they basically used magma so most of the funcitons are from magma calls


------


you have to provide the developers some performance indicators or something like that,
you are using this percentage so your efficiency level is this much
this funcctions are using this percentage of time
if they run the code they can see the runtime by their own
so if you can figure out which function takes this amoutn of time and if you report that, it would be helpful

collecting this type of information takes long time, if you try to get that, then you see your profiling time significantly increases
if you see

using 'nvprof --matrix' you'll see how long it is taking to collect the thing.

nvprof is slow profler when you collect detailed information. it does fast when showing average.

--------

he doesn't have any experience in using the spack upstream functionality
he mostly used separate spack environment on Summit.
mentioned it took long time to compile.

