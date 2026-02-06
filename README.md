# Mini-Cloud Local Portable Storage

A lightweight, self-hosted cloud storage solution built with FastAPI, perfect for Raspberry Pi and other portable devices.

## 🌟 Features

- **Fast & Lightweight**: Built with FastAPI for high performance
- **Portable**: Runs on Raspberry Pi, x86, ARM devices
- **Docker Support**: Easy deployment with Docker and Docker Compose
- **Web Interface**: Beautiful, responsive web UI for file management
- **RESTful API**: Complete API for programmatic access
- **Basic Authentication**: Secure access with HTTP Basic Auth
- **File Management**: Upload, download, delete files and create folders
- **Directory Navigation**: Browse through folders with ease
- **Storage Statistics**: View total storage usage and file count

## 🚀 Quick Start

### Using Docker Compose (Recommended)

1. Clone the repository:
```bash
git clone https://github.com/Ahmedmecatronique/home-container-drive.git
cd home-container-drive
```

2. Create environment file:
```bash
cp .env.example .env
```

3. Edit `.env` and set your credentials:
```env
SECRET_KEY=your-secret-key-here
API_USERNAME=admin
API_PASSWORD=your-secure-password
```

4. Start the service:
```bash
docker-compose up -d
```

5. Access the web interface at `http://localhost:8000`

### Manual Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create `.env` file:
```bash
cp .env.example .env
```

3. Run the application:
```bash
python main.py
```

## 📦 Raspberry Pi Setup

### Prerequisites

- Raspberry Pi 3/4/5 with Raspberry Pi OS
- Docker and Docker Compose installed

### Installation on Raspberry Pi

1. Install Docker:
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

2. Install Docker Compose:
```bash
sudo apt-get update
sudo apt-get install -y docker-compose
```

3. Clone and run:
```bash
git clone https://github.com/Ahmedmecatronique/home-container-drive.git
cd home-container-drive
cp .env.example .env
# Edit .env with your credentials
docker-compose up -d
```

4. Access from any device on your network at `http://<raspberry-pi-ip>:8000`

## 🔧 Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST` | 0.0.0.0 | Server host |
| `PORT` | 8000 | Server port |
| `SECRET_KEY` | - | Secret key for security |
| `API_USERNAME` | admin | API username |
| `API_PASSWORD` | admin | API password |
| `STORAGE_PATH` | ./storage | Storage directory path |
| `MAX_UPLOAD_SIZE` | 104857600 | Max upload size (100MB) |
| `CORS_ORIGINS` | * | CORS allowed origins |

## 📚 API Documentation

Once running, access the interactive API documentation at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### API Endpoints

- `GET /api/health` - Health check
- `GET /api/storage/info` - Get storage statistics
- `GET /api/files?path=<path>` - List files in directory
- `POST /api/files/upload?path=<path>` - Upload file
- `GET /api/files/download?path=<path>` - Download file
- `DELETE /api/files?path=<path>` - Delete file or directory
- `POST /api/directories?path=<path>` - Create directory

### Authentication

All API endpoints (except `/` and `/api/health`) require HTTP Basic Authentication:

```bash
curl -u admin:admin http://localhost:8000/api/storage/info
```

## 🖥️ Usage Examples

### Upload a file using curl:
```bash
curl -u admin:admin -F "file=@document.pdf" http://localhost:8000/api/files/upload
```

### Download a file:
```bash
curl -u admin:admin http://localhost:8000/api/files/download?path=document.pdf -o downloaded.pdf
```

### List files:
```bash
curl -u admin:admin http://localhost:8000/api/files
```

### Create a directory:
```bash
curl -u admin:admin -X POST http://localhost:8000/api/directories?path=my-folder
```

### Delete a file:
```bash
curl -u admin:admin -X DELETE http://localhost:8000/api/files?path=document.pdf
```

## 🔒 Security Considerations

1. **Change default credentials** in `.env` file
2. **Use strong passwords** for production
3. **Use HTTPS** in production (consider using a reverse proxy like nginx)
4. **Limit CORS origins** in production by setting specific domains
5. **Set appropriate file size limits** based on your storage capacity

## 📁 Project Structure

```
home-container-drive/
├── main.py              # FastAPI application
├── config.py            # Configuration settings
├── storage_service.py   # File storage service
├── auth.py              # Authentication logic
├── requirements.txt     # Python dependencies
├── Dockerfile           # Docker image definition
├── docker-compose.yml   # Docker Compose configuration
├── .env.example         # Example environment file
├── .gitignore          # Git ignore rules
├── .dockerignore       # Docker ignore rules
├── static/             # Web interface
│   └── index.html      # Frontend UI
└── storage/            # File storage directory (created at runtime)
```

## 🛠️ Development

### Running in development mode:
```bash
# Install dependencies
pip install -r requirements.txt

# Run with auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Building Docker image:
```bash
docker build -t mini-cloud-storage .
```

## 📝 License

MIT License - feel free to use this project for personal or commercial purposes.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📞 Support

For issues and questions, please use the GitHub Issues page.
