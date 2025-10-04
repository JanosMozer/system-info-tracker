from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.security import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
import yaml
import metrics

# --- Configuration ---
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

API_KEY = config.get("security", {}).get("api_key")
API_KEY_NAME = "X-API-KEY"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

app = FastAPI(
    title="SLURM & System Info Tracker",
    description="A web dashboard to monitor a SLURM cluster and system resources.",
    version="1.0.0"
)

# Add CORS middleware to allow React app to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for simplicity
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="public"), name="static")

async def verify_api_key(x_api_key: str = Depends(api_key_header)):
    """Dependency to verify the API key."""
    if not API_KEY:
        # If no API key is configured, allow access.
        return
    if not x_api_key or x_api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API Key"
        )

# --- API Routes ---
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """
    Serves the main dashboard HTML page with live system data.
    """
    poll_interval = config.get("monitoring", {}).get("poll_interval_seconds", 10)
    
    # Generate HTML page with live data
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>System Info Tracker Dashboard</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <style>
            .metric-card {{ 
                transition: all 0.3s ease; 
            }}
            .metric-card:hover {{ 
                transform: translateY(-2px); 
                box-shadow: 0 8px 25px rgba(0,0,0,0.15); 
            }}
            .status-running {{ color: #10b981; }}
            .status-pending {{ color: #f59e0b; }}
            .status-failed {{ color: #ef4444; }}
            .gpu-hot {{ background-color: #fee2e2; border-color: #ef4444; }}
        </style>
    </head>
    <body class="bg-gray-100 min-h-screen">
        <div class="container mx-auto px-4 py-8">
            <h1 class="text-4xl font-bold text-gray-800 mb-8">System Info Tracker Dashboard</h1>
            
            <!-- System Stats -->
            <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                <div class="metric-card bg-white rounded-lg shadow-lg p-6">
                    <h3 class="text-lg font-semibold text-gray-700 mb-2">CPU Usage</h3>
                    <div class="text-3xl font-bold text-blue-600" id="cpu-usage">--.--%</div>
                </div>
                <div class="metric-card bg-white rounded-lg shadow-lg p-6">
                    <h3 class="text-lg font-semibold text-gray-700 mb-2">Memory Usage</h3>
                    <div class="text-3xl font-bold text-green-600" id="memory-usage">--.--%</div>
                    <div class="text-sm text-gray-500" id="memory-details">-- / -- GB</div>
                </div>
                <div class="metric-card bg-white rounded-lg shadow-lg p-6">
                    <h3 class="text-lg font-semibold text-gray-700 mb-2">Last Updated</h3>
                    <div class="text-lg font-semibold text-gray-600" id="last-updated">--:--:--</div>
                </div>
            </div>

            <!-- GPU Stats -->
            <div class="mb-8">
                <h2 class="text-2xl font-bold text-gray-800 mb-4">GPU Status</h2>
                <div id="gpu-container" class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div class="bg-white rounded-lg shadow-lg p-6">
                        <div class="text-gray-500">No GPU data available</div>
                    </div>
                </div>
            </div>

            <!-- SLURM Jobs -->
            <div class="mb-8">
                <h2 class="text-2xl font-bold text-gray-800 mb-4">SLURM Jobs</h2>
                <div class="bg-white rounded-lg shadow-lg overflow-hidden">
                    <div class="overflow-x-auto">
                        <table class="min-w-full">
                            <thead class="bg-gray-50">
                                <tr>
                                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Job ID</th>
                                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Name</th>
                                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">User</th>
                                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">State</th>
                                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">CPUs</th>
                                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Memory</th>
                                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Node</th>
                                </tr>
                            </thead>
                            <tbody id="jobs-tbody" class="bg-white divide-y divide-gray-200">
                                <tr>
                                    <td colspan="7" class="px-6 py-4 text-center text-gray-500">No SLURM jobs available</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>

        <script>
            async function fetchMetrics() {{
                try {{
                    const response = await fetch('/api/metrics');
                    const data = await response.json();
                    updateUI(data);
                }} catch (error) {{
                    console.error('Error fetching metrics:', error);
                }}
            }}

            function updateUI(data) {{
                // Update system stats
                const systemStats = data.system_stats || {{}};
                document.getElementById('cpu-usage').textContent = 
                    systemStats.cpu_usage_percent !== undefined && systemStats.cpu_usage_percent !== null ? 
                    systemStats.cpu_usage_percent.toFixed(1) + '%' : '--.--%';
                document.getElementById('memory-usage').textContent = 
                    systemStats.memory_usage_percent !== undefined && systemStats.memory_usage_percent !== null ? 
                    systemStats.memory_usage_percent.toFixed(1) + '%' : '--.--%';
                document.getElementById('memory-details').textContent = 
                    systemStats.memory_used_gb !== undefined && systemStats.memory_total_gb !== undefined ? 
                    `${{systemStats.memory_used_gb}} / ${{systemStats.memory_total_gb}} GB` : '-- / -- GB';

                // Update GPU stats
                const gpuStats = data.gpu_stats || [];
                const gpuContainer = document.getElementById('gpu-container');
                if (gpuStats.length > 0) {{
                    gpuContainer.innerHTML = gpuStats.map(gpu => `
                        <div class="bg-white rounded-lg shadow-lg p-6 ${{gpu.is_hot ? 'gpu-hot' : ''}}">
                            <h4 class="font-semibold text-gray-800">${{gpu.gpu_name || '--'}}</h4>
                            <div class="mt-2 space-y-1">
                                <div class="flex justify-between">
                                    <span class="text-gray-600">Temperature:</span>
                                    <span class="font-medium">${{gpu.temperature !== undefined && gpu.temperature !== null ? gpu.temperature + '°C' : '--°C'}}</span>
                                </div>
                                <div class="flex justify-between">
                                    <span class="text-gray-600">GPU Usage:</span>
                                    <span class="font-medium">${{gpu.gpu_utilization !== undefined && gpu.gpu_utilization !== null ? gpu.gpu_utilization + '%' : '--%'}}</span>
                                </div>
                                <div class="flex justify-between">
                                    <span class="text-gray-600">Memory:</span>
                                    <span class="font-medium">${{
                                        (gpu.memory_used !== undefined && gpu.memory_used !== null && gpu.memory_total !== undefined && gpu.memory_total !== null) ?
                                        `${{gpu.memory_used}} / ${{gpu.memory_total}} MB` : '-- / -- MB'
                                    }}</span>
                                </div>
                            </div>
                        </div>
                    `).join('');
                }} else {{
                    gpuContainer.innerHTML = '<div class="bg-white rounded-lg shadow-lg p-6"><div class="text-gray-500">No GPU data available</div></div>';
                }}

                // Update SLURM jobs
                const jobs = data.slurm_jobs || [];
                const jobsTbody = document.getElementById('jobs-tbody');
                if (jobs.length > 0) {{
                    jobsTbody.innerHTML = jobs.map(job => `
                        <tr>
                            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">${{job.id || '--'}}</td>
                            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${{job.name || '--'}}</td>
                            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${{job.user || '--'}}</td>
                            <td class="px-6 py-4 whitespace-nowrap text-sm">
                                <span class="status-${{job.state ? job.state.toLowerCase() : 'unknown'}}">${{job.state || '--'}}</span>
                            </td>
                            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${{job.cpus || '--'}}</td>
                            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${{job.memory || '--'}}</td>
                            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${{job.nodelist || '--'}}</td>
                        </tr>
                    `).join('');
                }} else {{
                    jobsTbody.innerHTML = '<tr><td colspan="7" class="px-6 py-4 text-center text-gray-500">No SLURM jobs available</td></tr>';
                }}

                // Update timestamp
                document.getElementById('last-updated').textContent = new Date().toLocaleTimeString();
            }}

            // Initial fetch
            fetchMetrics();

            // Auto-refresh every {poll_interval} seconds
            setInterval(fetchMetrics, {poll_interval * 1000});
        </script>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html_content)

@app.get("/api/metrics")
async def get_metrics_data(dependencies=[Depends(verify_api_key)]):
    """
    Provides all monitored data in JSON format.
    This endpoint is protected by an API key if one is configured.
    """
    return metrics.get_all_metrics()
