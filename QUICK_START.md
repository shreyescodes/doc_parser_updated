# 🚀 Quick Start Guide

Get your LP Document Parser up and running in minutes!

## Prerequisites

- **Python 3.11+**
- **PostgreSQL 12+**
- **Git**

## Installation Steps

### 1. Clone and Setup

```bash
# Clone the repository (if not already done)
git clone <your-repo-url>
cd doc-parser

# Install dependencies
pip install -r requirements.txt
```

### 2. Database Setup

#### Option A: Automated Setup (Recommended)

```bash
# Copy environment file
cp env.example .env

# Edit .env with your database credentials
# DATABASE_URL=postgresql://username:password@localhost:5432/doc_parser

# Run automated setup
python scripts/setup_db.py
```

#### Option B: Docker Setup

```bash
# Navigate to docker directory
cd deployment/docker

# Start all services
docker-compose up -d

# Check status
docker-compose ps
```

### 3. Start the Application

```bash
# Run the application
python main.py
```

### 4. Access the Application

- **API Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

### 5. Login

Default admin credentials:
- **Username**: `admin`
- **Password**: `admin123`

⚠️ **Change the default password immediately!**

## Quick Commands

### Database Management

```bash
# Check database health
python scripts/check_db.py

# Reset database (⚠️ deletes all data)
python scripts/reset_db.py

# Create new user
python scripts/create_user.py username email password --admin
```

### Development

```bash
# Run with auto-reload
uvicorn app.main:app --reload

# Run tests
pytest

# Format code
black .
isort .
```

### Docker Commands

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f app

# Stop services
docker-compose down

# Rebuild and start
docker-compose up --build -d
```

## API Usage Examples

### 1. Upload Document

```bash
curl -X POST "http://localhost:8000/documents/upload" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -F "file=@capital_call.pdf"
```

### 2. Process Document

```bash
curl -X POST "http://localhost:8000/documents/1/process" \
     -H "Authorization: Bearer YOUR_TOKEN"
```

### 3. Get Document Details

```bash
curl -X GET "http://localhost:8000/documents/1" \
     -H "Authorization: Bearer YOUR_TOKEN"
```

### 4. Get Capital Call Details

```bash
curl -X GET "http://localhost:8000/documents/1/capital-call" \
     -H "Authorization: Bearer YOUR_TOKEN"
```

## Troubleshooting

### Common Issues

#### Database Connection Failed
```bash
# Check database status
python scripts/check_db.py

# Ensure PostgreSQL is running
sudo systemctl start postgresql  # Linux
brew services start postgresql   # macOS
```

#### Migration Errors
```bash
# Reset database
python scripts/reset_db.py

# Or manually fix migrations
alembic upgrade head
```

#### Port Already in Use
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Or use different port
uvicorn app.main:app --port 8001
```

### Environment Issues

#### Missing Dependencies
```bash
# Install system dependencies (Ubuntu/Debian)
sudo apt-get install tesseract-ocr poppler-utils

# Install system dependencies (macOS)
brew install tesseract poppler
```

#### Permission Errors
```bash
# Make scripts executable
chmod +x scripts/*.py

# Fix upload directory permissions
chmod 755 uploads/
```

## Development Workflow

### 1. Make Changes

Edit your code in the `app/` directory.

### 2. Test Changes

```bash
# Run tests
pytest

# Check code style
black --check .
isort --check .
```

### 3. Database Changes

```bash
# Create migration
alembic revision --autogenerate -m "Description"

# Apply migration
alembic upgrade head
```

### 4. Deploy

```bash
# Build Docker image
docker build -f deployment/docker/Dockerfile -t doc-parser .

# Or use docker-compose
docker-compose up --build -d
```

## Production Deployment

### 1. Environment Configuration

```bash
# Copy production environment
cp env.example .env.prod

# Update with production values
SECRET_KEY=your-super-secret-key
DATABASE_URL=postgresql://user:pass@prod-db:5432/doc_parser
MINIO_SECRET_KEY=your-minio-secret
```

### 2. Security Checklist

- [ ] Change default passwords
- [ ] Use strong SECRET_KEY
- [ ] Enable HTTPS
- [ ] Configure firewall
- [ ] Set up monitoring
- [ ] Enable backups

### 3. Scale Services

```bash
# Scale workers
docker-compose up --scale celery-worker=3

# Use load balancer
# Configure nginx for multiple app instances
```

## Support

### Documentation

- **Database Setup**: [docs/DATABASE_SETUP.md](docs/DATABASE_SETUP.md)
- **API Documentation**: http://localhost:8000/docs
- **Main README**: [README.md](README.md)

### Getting Help

1. Check the logs: `logs/app.log`
2. Run health check: `python scripts/check_db.py`
3. Review error messages
4. Check database connectivity
5. Verify environment configuration

### Common Commands Reference

```bash
# Database
python scripts/setup_db.py      # Initial setup
python scripts/check_db.py      # Health check
python scripts/reset_db.py      # Reset (⚠️ destructive)
alembic upgrade head           # Apply migrations

# Application
python main.py                 # Start app
uvicorn app.main:app --reload  # Development mode

# Docker
docker-compose up -d          # Start services
docker-compose down           # Stop services
docker-compose logs -f app    # View logs

# Users
python scripts/create_user.py username email password --admin
```

## Next Steps

1. **Configure your environment** in `.env`
2. **Upload test documents** via the API
3. **Customize extraction rules** for your document types
4. **Set up monitoring** and alerts
5. **Configure backups** for production

Happy parsing! 🎉
