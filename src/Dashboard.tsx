import React, { useState, useEffect } from 'react';
import { MetricsData, GpuStats, mockData } from './mockData';

const Dashboard: React.FC = () => {
  const [data, setData] = useState<MetricsData>(mockData);
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [useRealData, setUseRealData] = useState<boolean>(false); // Toggle between mock and real data

  const fetchRealData = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await fetch('http://localhost:8080/api/metrics');
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const realData = await response.json();
      setData(realData);
      setLastUpdate(new Date());
    } catch (err) {
      console.error('Failed to fetch real data:', err);
      setError('Failed to fetch data from Python backend. Using mock data.');
      // Fall back to mock data if real data fails
      setData(mockData);
    } finally {
      setIsLoading(false);
    }
  };

  // Fetch data (real or mock) every 10 seconds
  useEffect(() => {
    const fetchData = () => {
      if (useRealData) {
        fetchRealData();
      } else {
        // Use mock data with slight randomization
        const updatedData = {
          ...mockData,
          system_stats: {
            ...mockData.system_stats,
            cpu_usage_percent: Math.max(0, Math.min(100, mockData.system_stats.cpu_usage_percent + (Math.random() - 0.5) * 10)),
            memory_usage_percent: Math.max(0, Math.min(100, mockData.system_stats.memory_usage_percent + (Math.random() - 0.5) * 5))
          }
        };
        setData(updatedData);
        setLastUpdate(new Date());
      }
    };

    // Initial fetch
    fetchData();

    // Set up interval
    const interval = setInterval(fetchData, 10000);
    return () => clearInterval(interval);
  }, [useRealData]);

  const SystemStatsCard: React.FC<{ title: string; value: string | number; unit?: string }> = ({ title, value, unit = '' }) => (
    <div className="bg-white p-6 rounded-lg shadow-md">
      <h3 className="font-bold text-gray-600 text-sm uppercase tracking-wide">{title}</h3>
      <p className="text-3xl font-bold text-gray-800 mt-2">{value}{unit}</p>
    </div>
  );

  const GpuCard: React.FC<{ gpu: GpuStats }> = ({ gpu }) => (
    <div className={`bg-white p-6 rounded-lg shadow-md ${gpu.is_hot ? 'border-l-4 border-red-500 bg-red-50' : ''}`}>
      <h4 className="font-bold text-gray-800 text-lg">{gpu.gpu_name}</h4>
      <div className="mt-4 space-y-2">
        <div className="flex justify-between">
          <span className="text-gray-600">Temperature:</span>
          <span className={`font-semibold ${gpu.temperature > 80 ? 'text-red-600' : 'text-green-600'}`}>
            {gpu.temperature}°C
          </span>
        </div>
        <div className="flex justify-between">
          <span className="text-gray-600">GPU Utilization:</span>
          <span className={`font-semibold ${gpu.gpu_utilization > 90 ? 'text-red-600' : 'text-blue-600'}`}>
            {gpu.gpu_utilization}%
          </span>
        </div>
        <div className="flex justify-between">
          <span className="text-gray-600">Memory Utilization:</span>
          <span className="font-semibold text-purple-600">{gpu.memory_utilization}%</span>
        </div>
        <div className="flex justify-between">
          <span className="text-gray-600">Memory:</span>
          <span className="font-semibold text-gray-800">
            {gpu.memory_used} / {gpu.memory_total} MiB
          </span>
        </div>
      </div>
      {gpu.is_hot && (
        <div className="mt-3 px-3 py-1 bg-red-100 text-red-800 text-sm rounded-full inline-block">
          🔥 High Usage
        </div>
      )}
    </div>
  );

  const getJobStateColor = (state: string) => {
    switch (state) {
      case 'RUNNING': return 'bg-green-100 text-green-800';
      case 'PENDING': return 'bg-yellow-100 text-yellow-800';
      case 'COMPLETED': return 'bg-blue-100 text-blue-800';
      case 'FAILED': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="min-h-screen bg-gray-100">
      <div className="container mx-auto p-6">
        {/* Header */}
        <header className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-800 mb-2">SLURM Cluster Dashboard</h1>
          <p className="text-gray-600">Real-time monitoring of jobs and system resources</p>
          
          {/* Data Source Toggle */}
          <div className="mt-4 flex items-center justify-center space-x-4">
            <button
              onClick={() => setUseRealData(!useRealData)}
              className={`px-4 py-2 rounded-lg font-semibold transition-colors ${
                useRealData 
                  ? 'bg-blue-600 text-white hover:bg-blue-700' 
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              {useRealData ? '🔴 Live Data' : '🟡 Mock Data'}
            </button>
            
            {isLoading && (
              <div className="flex items-center text-blue-600">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600 mr-2"></div>
                Loading...
              </div>
            )}
            
            {error && (
              <div className="text-red-600 text-sm max-w-md">
                ⚠️ {error}
              </div>
            )}
          </div>
          
          <p className="text-sm text-gray-500 mt-2">
            Last updated: {lastUpdate.toLocaleTimeString()}
            {useRealData && ' (from Python backend)'}
          </p>
        </header>

        {/* System Stats */}
        <section className="mb-8">
          <h2 className="text-2xl font-semibold mb-4 text-gray-700">System Overview</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <SystemStatsCard 
              title="CPU Usage" 
              value={data.system_stats.cpu_usage_percent.toFixed(1)} 
              unit="%" 
            />
            <SystemStatsCard 
              title="Memory Usage" 
              value={data.system_stats.memory_usage_percent.toFixed(1)} 
              unit="%" 
            />
            <SystemStatsCard 
              title="Memory Used" 
              value={data.system_stats.memory_used_gb.toFixed(1)} 
              unit=" GB" 
            />
            <SystemStatsCard 
              title="Total Memory" 
              value={data.system_stats.memory_total_gb.toFixed(1)} 
              unit=" GB" 
            />
          </div>
        </section>

        {/* GPU Stats */}
        <section className="mb-8">
          <h2 className="text-2xl font-semibold mb-4 text-gray-700">GPU Status</h2>
          {data.gpu_stats.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {data.gpu_stats.map((gpu) => (
                <GpuCard key={gpu.uuid} gpu={gpu} />
              ))}
            </div>
          ) : (
            <div className="bg-white p-6 rounded-lg shadow-md">
              <p className="text-gray-500 text-center">No GPUs detected</p>
            </div>
          )}
        </section>

        {/* SLURM Jobs */}
        <section>
          <h2 className="text-2xl font-semibold mb-4 text-gray-700">SLURM Jobs</h2>
          <div className="bg-white rounded-lg shadow-md overflow-hidden">
            {data.slurm_jobs.length > 0 ? (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Job ID</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Name</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">User</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">State</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Nodes</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">CPUs</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Memory</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Walltime</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {data.slurm_jobs.map((job) => (
                      <tr key={job.id} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{job.id}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{job.name}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{job.user}</td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getJobStateColor(job.state)}`}>
                            {job.state}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{job.nodes}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{job.cpus}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{job.memory}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{job.walltime}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="p-6 text-center">
                <p className="text-gray-500">No SLURM jobs found</p>
              </div>
            )}
          </div>
        </section>
      </div>
    </div>
  );
};

export default Dashboard;
