#!/bin/bash
#SBATCH --job-name=recording_conversion
#SBATCH --time=01:30:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=24
#SBATCH --mem-per-cpu=3G
#SBATCH --output=recording_conversion_%j.out
#SBATCH --error=recording_conversion_%j.err
#SBATCH --tmp=100g

set -e

echo "[$(date)] Job started on $(hostname)"

# Load Python
echo "[$(date)] Loading modules..."
module load stack/2024-06
module load python/3.12.8

# Activate environment
echo "[$(date)] Activating virtual environment..."
cd $HOME/conlyse
source venv/bin/activate

# Copy Data to TMP
echo "[$(date)] Copying data to node-local storage..."
rsync -aq ${SCRATCH}/converted_recordings.zip ${TMPDIR}/

cd $TMPDIR
echo "[$(date)] Unzipping archive..."
unzip -q converted_recordings.zip
rm converted_recordings.zip

# Run conversion
echo "[$(date)] Running recording conversion..."
recording-converter \
  --recording-dir converted_recordings \
  --output-dir replays \
  --mode rur \
  --bulk \
  --processes $SLURM_CPUS_PER_TASK \
  --overwrite


echo "[$(date)] Loading modules for compression..."
module load stack/2025-06
module load pigz/2.8

echo "[$(date)] Compressing replays directory..."
tar cf - replays | pigz -p $SLURM_CPUS_PER_TASK > replays.tar.gz


# Copy results back
echo "[$(date)] Copying results back to SCRATCH..."

rsync -aq --delete ${TMPDIR}/replays/ ${SCRATCH}/replays/
rsync -aq ${TMPDIR}/replays.tar.gz ${SCRATCH}/replays.tar.gz

echo "[$(date)] Job finished!"