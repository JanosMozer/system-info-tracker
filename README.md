# SLURM & System Info Tracker

A lightweight, self-contained web dashboard to monitor the status of a SLURM cluster and system resources. It provides real-time insights into queued and running jobs, GPU statistics, and node-level CPU/memory usage.

![Dashboard Screenshot](https://i.imgur.com/your-screenshot.png) <!--- This is a placeholder for a screenshot -->

## Features

- **SLURM Job Monitoring:** View details of queued and running jobs, including Job ID, name, user, state, and resource requests.
- **GPU Statistics:** Monitor NVIDIA GPU utilization, memory usage, and temperature. Hot GPUs are highlighted.
- **System Resource Tracking:** Keep an eye on overall CPU and memory usage of the node.
- **Web Dashboard:** A clean, modern UI built with FastAPI and Tailwind CSS that updates automatically.
- **REST API:** A JSON endpoint to fetch all monitoring data for external use.
- **Configurable:** Easily configure the server port, polling interval, and an optional API key via a `config.yaml` file.
- **Tailscale Integration:** Simple instructions to make your dashboard accessible over your private Tailscale network.

## Project Structure

```
.
├── config.yaml         # Configuration file
├── dashboard.py        # FastAPI web server and frontend logic
├── main.py             # Main entry point to start the server
├── metrics.py          # Data collection from SLURM and system
├── README.md           # This file
├── requirements.txt    # Python dependencies
└── templates
    └── index.html      # HTML template for the dashboard
```

## Setup and Installation

### 1. Prerequisites

- Python 3.7+
- A SLURM cluster environment
- `nvidia-smi` CLI for GPU monitoring (if applicable)

### 2. Clone the Repository

```bash
git clone <your-repo-url>
cd system-info-tracker
```

### 3. Install Dependencies

Create a virtual environment (recommended) and install the required Python packages.

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 4. Configuration

Edit the `config.yaml` file to customize the application settings.

```yaml
server:
  host: "0.0.0.0"  # Host to bind the server to
  port: 8080         # Port to run the server on

monitoring:
  poll_interval_seconds: 10  # How often to refresh data

security:
  api_key: "your-secret-api-key" # Leave empty to disable API key
```

### 5. Using Live Data

By default, the application runs with mock data for demonstration purposes. To use live data from your cluster, you need to edit `metrics.py`:

- Open `metrics.py`.
- Change `USE_MOCK_DATA = True` to `USE_MOCK_DATA = False`.

This will enable the script to call `squeue` and `nvidia-smi` directly.

## Running the Application

Once the dependencies are installed and the configuration is set, you can start the server:

```bash
python main.py
```

You should see an output indicating that the server is running:

```
Starting server at http://0.0.0.0:8080
```

Now you can access the dashboard in your web browser at `http://<your-server-ip>:8080`.

## Accessing via Tailscale

Tailscale is a great way to securely access your dashboard from any of your devices, wherever you are.

### 1. Install Tailscale

Follow the instructions to [install Tailscale](https://tailscale.com/download/) on the cluster node where the dashboard is running, and on the device you want to access it from (e.g., your laptop or phone).

### 2. Start Tailscale

On the cluster node, start Tailscale and log in:

```bash
sudo tailscale up
```

### 3. Find your Tailscale IP

Find the Tailscale IP address of your cluster node:

```bash
tailscale ip -4
```

This will give you an IP address in the `100.x.x.x` range.

### 4. Access the Dashboard

On your other device (also connected to Tailscale), open a web browser and navigate to the dashboard using the Tailscale IP and the configured port:

`http://<your-tailscale-ip>:8080`

And that's it! Your dashboard is now securely accessible over your private network.

## API Usage

The dashboard exposes a REST API endpoint at `/api/metrics` to fetch all the monitored data in JSON format.

If an `api_key` is set in `config.yaml`, you must include it in the `X-API-KEY` header of your request.

**Example using `curl`:**

```bash
curl -H "X-API-KEY: your-secret-api-key" http://localhost:8080/api/metrics
```
