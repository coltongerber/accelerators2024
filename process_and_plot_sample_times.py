from glob import iglob
import pandas as pd
import re
import os
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np


plt.close('all')
cmap = mpl.colormaps['tab10']
colors = cmap.colors

for tests, ncores in [('mpi', 8), ('mpi', 36), ('cuda', 1)]:
    # Set variable for where to read test output files from
    if tests == 'cuda':
        dirs = ['../QUICK-master_cuda/cuda_samples/', '../QUICK-master_cuda_commented/cuda_samples/']
    elif tests == 'mpi':
        dirs = [f'../QUICK-master_mpi/mpi_samples_{ncores}/', f'../QUICK-master_mpi_commented/mpi_samples_{ncores}/']

    # dirs contains one folder with tests that did receive octree pruning and one folder with tests that did not.
    for dir in dirs:
        columns = []
        rows = []
        files = [x for x in iglob(os.path.join(dir, 'ene_psb3_b3lyp_631gss.out*'))]
        # Iterate over all 10 test output files
        for i in range(len(files)):
            path = files[i]
            with open(path, 'r') as file:
                lines = file.readlines()
            # Find where in test output file the timing information starts
            for j in range(len(lines)):
                line = lines[j]
                if 'TIMING' in line:
                    timing_start = j
                    break
            data = []
            lines = lines[timing_start+1:timing_start+23]
            # Process the timing lines into labels and times, adding each pair to a list
            for line in lines:
                splitline = line.split('=')
                name = splitline[0].split('|')[1]
                name = name.strip()
                if name == 'TOTAL TIME' or name == 'TOTAL OPERATOR REDUCTION TIME':
                    continue
                values = splitline[1]
                if '(' in values:
                    values = values.split('(')
                    raw = float(values[0].strip())
                if i == 0:
                    columns.append(name)
                data.append(raw)
            rows.append(data)
        df = pd.DataFrame(rows, columns=columns)
        if 'commented' in dir:
            commented_df = df.copy()
        else:
            normal_df = df.copy()

    # Make a figure comparing timing between 'normal' (with octree pruning) and 'commented' (without octree pruning)
    fig, ax = plt.subplots(layout='constrained')
    i = 0
    width = 0.25  # the width of the bars
    multiplier = 1
    x = np.arange(len(commented_df.columns))
    labels = ['Normal', 'w/o Pruning']

    for df in [normal_df, commented_df]:
        describe = df.describe()
        offset = (width * multiplier) / 2
        rects = ax.barh(x+offset, describe.loc['mean'], width, color=colors[i], label=labels[i], alpha=0.5)
        plt.errorbar(describe.loc['mean'], x+offset, xerr=describe.loc['std'], color=colors[i], fmt='o', capsize=1, elinewidth=1, markersize=0 )
        i+=1
        multiplier-=2

    plt.yticks(x, describe.loc['mean'].index)
    plt.xlabel("Average Time [s]")
    plt.legend(loc='upper right')
    ax.set_xlim([0, 4.5])
    plt.savefig(f'{tests}_{ncores}_samples_analysis.png', dpi=600)

    commented_df.to_json(f'{tests}_{ncores}_commented_tests_df.json')
    normal_df.to_json(f'{tests}_{ncores}_normal_tests_df.json')


# Make a figure comparing MPI and CUDA
fig, ax = plt.subplots(layout='constrained')
mpi_df = pd.read_json('mpi_36_normal_tests_df.json')
cuda_df = pd.read_json('cuda_1_normal_tests_df.json')
i=0
multiplier = 1
labels = ['CPU (36 cores)', 'GPU']
for df in [mpi_df, cuda_df]:
    describe = df.describe()
    offset = (width * multiplier) / 2
    rects = ax.barh(x+offset, describe.loc['mean'], width, color=colors[i+2], label=labels[i], alpha=0.5)
    plt.errorbar(describe.loc['mean'], x+offset, xerr=describe.loc['std'], color=colors[i+2], fmt='o', capsize=1, elinewidth=1, markersize=0 )
    i+=1
    multiplier-=2
    
plt.yticks(x, describe.loc['mean'].index)
plt.xlabel("Average Time [s]")
plt.legend(loc='upper right')
ax.set_xlim([0, 4.5])
plt.savefig(f'mpi_vs_cuda_analysis.png', dpi=600)

'''
Example timing output in test output, for reference.
------------- TIMING ---------------
| INITIALIZATION TIME =     0.395549000( 11.19%)
| INITIAL GUESS TIME  =     0.970753000( 27.47%)
| OVERLAP 1e INTEGRALS TIME      =     0.007067000( 0.20%)
| OVERLAP 1e DIAGONALIZATION TIME =     0.654042000(18.51%)
| DFT GRID OPERATIONS =     0.073380000(  2.08%)
|       TOTAL GRID FORMATION TIME   =     0.001263000(  0.04%)
|       TOTAL GRID WEIGHT TIME      =     0.010014000(  0.28%)
|       TOTAL OCTREE RUN TIME       =     0.040000000(  1.13%)
|       TOTAL PRESCREENING TIME     =     0.000000000(  0.00%)
|       TOTAL DATA PACKING TIME     =     0.022103000(  0.63%)
| TOTAL SCF TIME      =     1.123090000( 31.78%)
|       TOTAL OP TIME      =     0.938447000( 26.55%)
|             TOTAL 1e TIME      =     0.027739000(  0.78%)
|                KINETIC 1e INTEGRALS TIME    =     0.027075000(  0.77%)
|                ATTRACTION 1e INTEGRALS TIME =     0.000583000(  0.02%)
|             TOTAL 2e TIME      =     0.338581000(  9.58%)
|             TOTAL EXC TIME     =     0.539426000( 15.26%)
|             TOTAL ENERGY TIME  =     0.000655000(  0.02%)
|       TOTAL DII TIME      =     0.183615000(  5.20%)
|             TOTAL DIAG TIME    =     0.144407000(  4.09%)
| DIPOLE TIME        =     0.064700000( 1.83%)
| TOTAL TIME          =     3.534383000
'''
