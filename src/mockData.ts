// Mock data types
export interface SlurmJob {
  id: string;
  name: string;
  user: string;
  state: 'RUNNING' | 'PENDING' | 'COMPLETED' | 'FAILED';
  nodes: number;
  cpus: number;
  memory: string;
  walltime: string;
  nodelist: string;
}

export interface GpuStats {
  uuid: string;
  gpu_name: string;
  temperature: number;
  memory_total: number;
  memory_used: number;
  memory_free: number;
  gpu_utilization: number;
  memory_utilization: number;
  is_hot: boolean;
}

export interface SystemStats {
  cpu_usage_percent: number;
  memory_usage_percent: number;
  memory_total_gb: number;
  memory_used_gb: number;
}

export interface MetricsData {
  slurm_jobs: SlurmJob[];
  gpu_stats: GpuStats[];
  system_stats: SystemStats;
}

// Mock data
export const mockData: MetricsData = {
  slurm_jobs: [
    {
      id: "72892",
      name: "bash",
      user: "user1",
      state: "RUNNING",
      nodes: 1,
      cpus: 1,
      memory: "500M",
      walltime: "3-00:00:00",
      nodelist: "gpu-node-01"
    },
    {
      id: "72893",
      name: "train_model",
      user: "user2",
      state: "RUNNING",
      nodes: 1,
      cpus: 8,
      memory: "16G",
      walltime: "2-12:00:00",
      nodelist: "gpu-node-02"
    },
    {
      id: "72894",
      name: "data_processing",
      user: "user1",
      state: "PENDING",
      nodes: 1,
      cpus: 2,
      memory: "4G",
      walltime: "4-00:00:00",
      nodelist: "(Resources)"
    },
    {
      id: "72895",
      name: "jupyter_notebook",
      user: "user3",
      state: "PENDING",
      nodes: 1,
      cpus: 4,
      memory: "8G",
      walltime: "7-00:00:00",
      nodelist: "(Priority)"
    }
  ],
  gpu_stats: [
    {
      uuid: "GPU-d49e29a8-3f5f-4a6d-9be2-4a4a5b6c7d8e",
      gpu_name: "NVIDIA GeForce RTX 3090",
      temperature: 55,
      memory_total: 24576,
      memory_used: 10240,
      memory_free: 14336,
      gpu_utilization: 80,
      memory_utilization: 42,
      is_hot: false
    },
    {
      uuid: "GPU-a1b2c3d4-e5f6-a7b8-c9d0-e1f2a3b4c5d6",
      gpu_name: "NVIDIA GeForce RTX 3090",
      temperature: 85,
      memory_total: 24576,
      memory_used: 20480,
      memory_free: 4096,
      gpu_utilization: 95,
      memory_utilization: 83,
      is_hot: true
    }
  ],
  system_stats: {
    cpu_usage_percent: 45.2,
    memory_usage_percent: 67.8,
    memory_total_gb: 32.0,
    memory_used_gb: 21.7
  }
};
