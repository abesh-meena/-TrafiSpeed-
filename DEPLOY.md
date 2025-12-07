# Traffic Speed Detection - Deployment Guide

## Docker Deployment (Recommended)

### Prerequisites
- Docker installed on your system
- Docker Compose (optional but recommended)

### Quick Start with Docker Compose

1. **Build and run the application:**
```bash
docker-compose up --build
```

2. **Access the application:**
Open your browser and go to: `http://localhost:5000`

### Manual Docker Deployment

1. **Build the Docker image:**
```bash
docker build -t speed-detection .
```

2. **Run the container:**
```bash
docker run -p 5000:5000 -v $(pwd)/uploads:/app/uploads -v $(pwd)/outputs:/app/outputs speed-detection
```

## Traditional Deployment

### Prerequisites
- Python 3.9+
- pip package manager

### Installation Steps

1. **Clone or download the project files**

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Create necessary directories:**
```bash
mkdir uploads outputs
```

4. **Run the application:**
```bash
python app.py
```

5. **Access the application:**
Open your browser and go to: `http://localhost:5000`

## Production Deployment

### Using Gunicorn (Recommended for production)

1. **Install gunicorn:**
```bash
pip install gunicorn
```

2. **Run with gunicorn:**
```bash
gunicorn --bind 0.0.0.0:5000 --workers 4 app:app
```

### Environment Variables

You can set these environment variables for production:

- `FLASK_ENV=production` - Set Flask to production mode
- `SECRET_KEY=your-secret-key` - Set a secure secret key

## Cloud Deployment Options

### Heroku
1. Install Heroku CLI
2. Create `Procfile`:
```
web: gunicorn --bind 0.0.0.0:$PORT app:app
```
3. Deploy:
```bash
heroku create
git add .
git commit -m "Deploy to Heroku"
git push heroku main
```

### AWS/Azure/GCP
- Use the provided Dockerfile
- Deploy as a container service
- Ensure port 5000 is exposed

## Important Notes

1. **File Storage**: Uploads and outputs are stored locally. For production, consider using cloud storage.
2. **Performance**: The speed detection is CPU-intensive. Consider using cloud instances with more CPU power.
3. **Security**: In production, add authentication and rate limiting.
4. **Scaling**: For multiple users, consider using a task queue for video processing.

## Troubleshooting

### Common Issues

1. **dlib installation fails**: 
   - Ensure you have cmake and build tools installed
   - On Ubuntu: `sudo apt-get install cmake build-essential`

2. **OpenCV issues**:
   - Install system dependencies: `sudo apt-get install libgtk-3-dev`

3. **Permission errors**:
   - Ensure the uploads and outputs directories have write permissions

4. **Port already in use**:
   - Change port in app.py or stop the service using port 5000

## Monitoring

- Check logs: `docker-compose logs -f` (for Docker)
- Monitor CPU usage during video processing
- Set up health checks for production deployment
