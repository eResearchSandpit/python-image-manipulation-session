#!/bin/bash
#SBATCH --job-name=image_process
#SBATCH --partition=quicktest
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=32
#SBATCH --time=5:00:00
#SBATCH --mem=10G

# Load the necessary modules
module load GCCcore/11.3.0
module load Python/3.10.4-bare

# Set the directory where the Python virtual environment will be created
ENVDIR="env"

# Create the Python virtual environment if it doesn't exist
if [ ! -d "$ENVDIR" ]; then
    python -m venv $ENVDIR
    source $ENVDIR/bin/activate
    pip install pillow
    deactivate
fi

# Activate the Python virtual environment
source $ENVDIR/bin/activate

# Run the Python script
python chatgpt-version/image_process.py

# Deactivate the Python virtual environment
deactivate
