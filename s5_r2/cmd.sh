# "queue.pl" uses qsub.  The options to it are
# options to qsub.  If you have GridEngine installed,
# change this to a queue you have access to.
# Otherwise, use "run.pl", which will run jobs locally
# (make sure your --num-jobs options are no more than
# the number of cpus on your machine.

# Select the backend used by run.sh from "local", "stdout", "sge", "slurm", or "ssh"
cmd_backend='local'

# Local machine, without any Job scheduling system
if [ "${cmd_backend}" = local ]; then
    export train_cmd="run.pl"
    export cuda_cmd="run.pl -l gpu=1"
    export decode_cmd="run.pl"
# "qsub" (Sun Grid Engine, or derivation of it)
elif [ "${cmd_backend}" = sge ]; then
    # The default setting is written in conf/queue.conf.
    # You must change "-q g.q" for the "queue" for your environment.
    # To know the "queue" names, type "qhost -q"
    # Note that to use "--gpu *", you have to setup "complex_value" for the system scheduler.
    export train_cmd="queue.pl -l 'arch=*64*'"
    export cuda_cmd="queue.pl -l gpu=1"
    export decode_cmd="queue.pl -l 'arch=*64*'"
# "sbatch" (Slurm)
elif [ "${cmd_backend}" = slurm ]; then
    # The default setting is written in conf/slurm.conf.
    # You must change "-p cpu" and "-p gpu" for the "partition" for your environment.
    # To know the "partion" names, type "sinfo".
    # You can use "--gpu * " by default for slurm and it is interpreted as "--gres gpu:*"
    # The devices are allocated exclusively using "${CUDA_VISIBLE_DEVICES}".
    export train_cmd="slurm.pl"
    export cuda_cmd="slurm.pl --num_threads 4 --mem 2G"
    export decode_cmd="slurm.pl"
else
    echo "$0: Error: Unknown cmd_backend=${cmd_backend}" 1>&2
    return 1
fi

#activate this if you want to run the corpus with gridengine (http://gridengine.org/)
#export train_cmd="queue.pl -l 'arch=*64*'"
#export decode_cmd="queue.pl -l 'arch=*64*'"
#export cuda_cmd="queue.pl -l gpu=1"

# export train_cmd="utils/run.pl"
# export decode_cmd="utils/run.pl"
# export cuda_cmd="utils/run.pl -l gpu=1"

# export train_cmd="utils/slurm.pl"
# export decode_cmd="utils/slurm.pl"
# export cuda_cmd="utils/slurm.pl --num_threads 28 --mem 2G"

# export sequitur_g2p="/usr/local/bin/g2p.py"
export sequitur_g2p="../../../venv/bin/g2p.py"
# default: 28
export nJobs=64
export nDecodeJobs=12
