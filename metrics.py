import subprocess
import pandas as pd
from io import StringIO
import psutil
import json
import os

# --- Mock Data ---
# Set this to False to use live data from shell commands
USE_MOCK_DATA = False

MOCK_SQUEUE_OUTPUT = """JOBID,NAME,USER,STATE,NODES,CPUS,MEMORY,SUBMIT_TIME,START_TIME,TIME_LEFT,NODELIST(REASON)
72892,bash,user1,RUNNING,1,1,500M,2025-10-04T10:00:00,2025-10-04T10:00:05,3-00:00:00,gpu-node-01
72893,train,user2,RUNNING,1,8,16G,2025-10-04T10:01:00,2025-10-04T10:01:10,2-12:00:00,gpu-node-02
72894,data,user1,PENDING,1,2,4G,2025-10-04T10:02:00,N/A,4-00:00:00,(Resources)
72895,jupyter,user3,PENDING,1,4,8G,2025-10-04T10:03:00,N/A,7-00:00:00,(Priority)
"""

MOCK_NVIDIA_SMI_OUTPUT = """uuid,name,temperature.gpu,memory.total,memory.used,memory.free,utilization.gpu,utilization.memory
GPU-d49e29a8-3f5f-4a6d-9be2-4a4a5b6c7d8e,NVIDIA GeForce RTX 3090,55,24576,10240,14336,80,42
GPU-a1b2c3d4-e5f6-a7b8-c9d0-e1f2a3b4c5d6,NVIDIA GeForce RTX 3090,65,24576,20480,4096,95,83
"""

def _run_command(command):
    """Executes a shell command and returns its output."""
    try:
        result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {command}")
        print(f"Stderr: {e.stderr}")
        return ""

def get_slurm_jobs():
    """
    Fetches SLURM job queue information using squeue.
    Returns a list of dictionaries, where each dictionary represents a job.
    """
    if USE_MOCK_DATA:
        output = MOCK_SQUEUE_OUTPUT
    else:
        squeue_format = "%.18i,%.80j,%.8u,%.9T,%.6D,%.4C,%.10m,%.20V,%.20S,%.10l,%R"
        command = f'squeue --format="{squeue_format}" --noheader'
        output = _run_command(command)
    
    if not output:
        return []

    # Add header for pandas since we use --noheader
    header = "JOBID,NAME,USER,STATE,NODES,CPUS,MEMORY,SUBMIT_TIME,START_TIME,TIME_LEFT,NODELIST(REASON)\n"
    output = header + output
    
    df = pd.read_csv(StringIO(output))
    df.rename(columns={
        'JOBID': 'id',
        'NAME': 'name',
        'USER': 'user',
        'STATE': 'state',
        'NODES': 'nodes',
        'CPUS': 'cpus',
        'MEMORY': 'memory',
        'SUBMIT_TIME': 'submit_time',
        'START_TIME': 'start_time',
        'TIME_LEFT': 'walltime',
        'NODELIST(REASON)': 'nodelist'
    }, inplace=True)

    return df.to_dict('records')


def get_gpu_stats():
    """
    Fetches GPU statistics using nvidia-smi.
    Returns a list of dictionaries, each representing a GPU.
    """
    if USE_MOCK_DATA:
        output = MOCK_NVIDIA_SMI_OUTPUT
    else:
        command = "nvidia-smi --query-gpu=uuid,name,temperature.gpu,memory.total,memory.used,memory.free,utilization.gpu,utilization.memory --format=csv,noheader,nounits"
        output = _run_command(command)
        # Add header for pandas
        header = "uuid,name,temperature.gpu,memory.total,memory.used,memory.free,utilization.gpu,utilization.memory\n"
        output = header + output

    if not output.strip():
        return []

    df = pd.read_csv(StringIO(output))
    df.columns = [col.strip() for col in df.columns]

    # Clean up column names that may have spaces
    df.rename(columns={
        'name': 'gpu_name',
        'temperature.gpu': 'temperature',
        'memory.total': 'memory_total',
        'memory.used': 'memory_used',
        'memory.free': 'memory_free',
        'utilization.gpu': 'gpu_utilization',
        'utilization.memory': 'memory_utilization'
    }, inplace=True)
    
    # Highlight heavily used GPUs
    df['is_hot'] = (df['temperature'] > 80) | (df['gpu_utilization'] > 90)

    return df.to_dict('records')

def get_system_stats():
    """
    Fetches system-wide CPU and memory statistics.
    """
    # Get CPU usage over a shorter interval for more responsive updates
    # but also check if there's any recent activity
    cpu_usage = psutil.cpu_percent(interval=0.1)
    if cpu_usage == 0.0:
        # If no activity detected, get average over last interval
        cpu_usage = psutil.cpu_percent(interval=None)
    
    memory_info = psutil.virtual_memory()
    
    # Handle NaN values that can't be JSON serialized
    cpu_usage = 0.0 if cpu_usage is None or cpu_usage != cpu_usage else cpu_usage
    memory_percent = 0.0 if memory_info.percent is None or memory_info.percent != memory_info.percent else memory_info.percent
    
    return {
        "cpu_usage_percent": round(cpu_usage, 1),
        "memory_usage_percent": round(memory_percent, 1),
        "memory_total_gb": round(memory_info.total / (1024**3), 2),
        "memory_used_gb": round(memory_info.used / (1024**3), 2)
    }

def get_all_metrics():
    """
    A helper function to aggregate all metrics from the different sources.
    """
    return {
        "slurm_jobs": get_slurm_jobs(),
        "gpu_stats": get_gpu_stats(),
        "system_stats": get_system_stats()
    }

if __name__ == '__main__':
    # For testing purposes
    all_metrics = get_all_metrics()
    print(json.dumps(all_metrics, indent=2))
