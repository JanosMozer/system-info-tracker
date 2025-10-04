import uvicorn
import yaml
from dashboard import app

if __name__ == "__main__":
    with open("config.yaml", "r") as f:
        config = yaml.safe_load(f)

    server_config = config.get("server", {})
    host = server_config.get("host", "0.0.0.0")
    port = server_config.get("port", 8080)

    print(f"Starting server at http://{host}:{port}")
    uvicorn.run(app, host=host, port=port)
