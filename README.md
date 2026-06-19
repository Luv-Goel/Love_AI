# Love AI System

A highly integrated AI infrastructure system consisting of an authentication gateway, proxy routing, web crawler logic, and search indexing tools.

## Architecture
- **Gateway** (`port 6666`): Handles API key generation, budget tracking, and initial request routing.
- **Love Smith** (`port 6665`): Proxy and middleware intercepts.
- **Love Engine** (`port 6667`): Core LLM management and cost tracking.
- **Love Crawler** (`port 6668`): Handles automated web reading operations.
- **Love Index**: Integrated search and indexing components.

## Getting Started

### Prerequisites
1. Set up your Python environment (`venv`).
2. Add your API credentials in a `.env` file (e.g. `NVIDIA_API_KEY`).

### Booting the System
You can start the entire stack using the provided PowerShell startup script:
```powershell
.\start_all.ps1
```

All backend logs will be printed to their respective `*.log` files in this directory.

## Testing & Usage
Once the system is running on your local loopback, navigate to the Gateway dashboard at `http://127.0.0.1:6666/admin/index.html` to generate API keys.
