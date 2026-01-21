# TimeShow Converter Tool

## Overview

**TimeShow Converter Tool** is a Python-based backend service for processing and converting TimeShow-related data into structured output formats.  
The application provides both a **command-line interface (CLI)** and a **high-performance REST API** built with **FastAPI**.

It is designed for server-side usage, automation pipelines, and high-load environments, supporting concurrent processing and batch operations.

---

## Key Features

- FastAPI-based REST API
- CLI tool for local and automated usage
- Single-file and batch processing
- Automatic ZIP archive generation for batch outputs
- Thread-safe and scalable (multi-worker support)
- Configurable behavior via `config.py`
- Load testing support using Locust
- Production-ready architecture

---

## Project Structure

```text
timeshow_converter_tool/
├── tsc.py                  # CLI processing entry point
├── tsc_api.py              # FastAPI web service
├── config.py               # Global configuration
├── requirements.txt        # Python dependencies
├── locustfile.py           # Load testing configuration
├── Outputs/                # Generated output files
├── curl_request_example.sh
├── curl_request_example.bat
└── README.md
```

---

## System Requirements

- Linux (Ubuntu 20.04+ recommended)
- Python 3.9+
- pip
- venv / virtualenv
- (Optional) Nginx
- (Optional) systemd

---

## Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd timeshow_converter_tool
```

Or upload and extract the ZIP archive on the server.

---

### 2. Create and Activate Virtual Environment

```bash
python3 -m venv env
source env/bin/activate
```

---

### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

## Usage

### CLI Mode

Run the converter manually:

```bash
python tsc.py
```

Run test mode:

```bash
python tsc.py test
```

---

### API Mode

Start the FastAPI server:

```bash
uvicorn tsc_api:app --host 0.0.0.0 --port 8081
```

Recommended production configuration:

```bash
uvicorn tsc_api:app \
  --host 0.0.0.0 \
  --port 8081 \
  --workers 4 \
  --log-level warning \
  --no-access-log
```

API will be available at:

```text
http://<server-ip>:8081
```

---

## API Documentation

When the server is running, automatic API documentation is available:

- Swagger UI: `http://<server-ip>:8081/docs`
- ReDoc: `http://<server-ip>:8081/redoc`

---

## Example API Request

```bash
curl -X POST http://localhost:8081/convert \
  -F "file=@input_file.ext"
```

(See `curl_request_example.sh` and `.bat` for more examples.)

---

## Output

- All generated files are stored in the `Outputs/` directory
- Batch processing results are automatically packed into ZIP archives

---

## Configuration

Application settings can be customized via `config.py`, including:

- Output paths
- Processing limits
- Performance-related options

---

## Load Testing

The project includes a Locust configuration for stress and load testing.

```bash
locust -f locustfile.py --host http://localhost:8081
```

Open in browser:

```text
http://localhost:8089
```

---

## Running as a systemd Service (Production)

Create a systemd service file:

```bash
sudo nano /etc/systemd/system/timeshow.service
```

```ini
[Unit]
Description=TimeShow Converter API
After=network.target

[Service]
User=www-data
WorkingDirectory=/opt/timeshow_converter_tool
ExecStart=/opt/timeshow_converter_tool/env/bin/uvicorn tsc_api:app \
    --host 127.0.0.1 \
    --port 8081 \
    --workers 4
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable timeshow
sudo systemctl start timeshow
sudo systemctl status timeshow
```

---

## Nginx Reverse Proxy Example

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8081;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

Reload Nginx:

```bash
sudo nginx -t
sudo systemctl reload nginx
```

---

## Production Recommendations

- Run behind **Nginx**
- Use **systemd** for service management
- Enable HTTPS (Let’s Encrypt)
- Adjust worker count based on CPU cores
- Monitor memory and CPU usage under load
