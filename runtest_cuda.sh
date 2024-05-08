#!/bin/bash -x
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH -p gpu
#SBATCH --export=ALL
#SBATCH --time=00:10:00
#SBATCH --job-name=runtest_cuda
#SBATCH -o out.%x
#SBATCH -e err.%x
#SBATCH --gres=gpu:v100:1

# Go to the directoy from which our job was launched
cd $SLURM_SUBMIT_DIR

module load apps/python3/2020.02
module load compilers/gcc/9.3.1
module load mpi/openmpi/gcc-cuda/4.1.2
module load libs/mkl/2021.1
conda activate my_env
source quick.rc

echo "running job"
START=$(date +%s.%N)
for i in {0..9}; do
nvprof --csv --log-file nvprof_cuda_%p.csv --profile-child-processes ./runtest --cuda
mv test/runs/cuda/ene_psb3_b3lyp_631gss.out cuda_samples/ene_psb3_b3lyp_631gss.out_$i
done

END=$(date +%s.%N)
echo "job has finished"
RUNTIME=$(echo "$END - $START" | bc -l)
echo ${RUNTIME} >> runtime_"${SLURM_JOB_NAME}".txt
