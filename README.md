# LP Document Parser

A comprehensive document parsing system for Limited Partner (LP) fiduciary documents, including capital call notices and distribution notices. Built with FastAPI, PostgreSQL, and privacy-first AI processing.

## Features

- **Document Processing**: Advanced document parsing using Docling and OCR
- **LP Document Classification**: Automatic classification of capital calls, distributions, and other LP documents
- **Structured Data Extraction**: Intelligent extraction of financial data, dates, amounts, and fund information
- **Privacy-First**: All processing happens locally - no data sent to external services
- **Scalable Architecture**: Docker-based deployment with PostgreSQL, Redis, and MinIO
- **Background Processing**: Celery-based task queue for document processing
- **RESTful API**: Comprehensive API for document management and processing

## Tech Stack

- **Backend**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Document Processing**: Docling + Tesseract OCR
- **Message Queue**: Redis + Celery
- **File Storage**: MinIO (S3-compatible)
- **Deployment**: Docker + Docker Compose
- **Reverse Proxy**: Nginx

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Git

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd doc-parser
```

2. Start the services:
```bash
docker-compose up -d
```

3. The API will be available at:
- API: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- MinIO Console: http://localhost:9001 (minioadmin/minioadmin)

### Environment Configuration

Copy the environment template and configure:
```bash
cp config.py.example .env
# Edit .env with your settings
```

## API Usage

### Upload Document

```bash
curl -X POST "http://localhost:8000/upload" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@capital_call.pdf"
```

### Process Document

```bash
curl -X POST "http://localhost:8000/documents/1/process"
```

### Get Document Details

```bash
curl -X GET "http://localhost:8000/documents/1"
```

### Get Capital Call Details

```bash
curl -X GET "http://localhost:8000/documents/1/capital-call"
```

### Get Distribution Details

```bash
curl -X GET "http://localhost:8000/documents/1/distribution"
```

## Document Types Supported

### Capital Call Notices
- Call dates and due dates
- Call amounts and percentages
- Fund information and commitments
- LP-specific contribution details
- Payment instructions and wire transfer info

### Distribution Notices
- Distribution dates and amounts
- Fund NAV and performance metrics
- LP-specific distribution amounts
- IRR and multiple calculations
- Payment methods and instructions

## Development

### Local Development Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Install system dependencies:
```bash
# Ubuntu/Debian
sudo apt-get install tesseract-ocr poppler-utils

# macOS
brew install tesseract poppler
```

3. Set up database:
```bash
# Start PostgreSQL
docker run -d --name postgres -e POSTGRES_PASSWORD=postgres -p 5432:5432 postgres:15

# Run migrations (when available)
alembic upgrade head
```

4. Start Redis:
```bash
docker run -d --name redis -p 6379:6379 redis:7
```

5. Run the application:
```bash
uvicorn main:app --reload
```

### Running Tests

```bash
pytest tests/
```

### Code Formatting

```bash
black .
isort .
```

## Architecture

### Core Components

1. **Document Processor**: Handles document parsing using Docling and OCR
2. **LP Extractor**: Specialized extraction for LP document types
3. **Database Models**: PostgreSQL models for documents, users, and extracted data
4. **API Endpoints**: RESTful API for document management
5. **Background Tasks**: Celery workers for async processing
6. **File Storage**: MinIO for document and processed data storage

### Processing Pipeline

1. **Upload**: Document uploaded via API
2. **Queue**: Document queued for background processing
3. **OCR**: Text extraction using Docling and Tesseract
4. **Classification**: Document type classification
5. **Extraction**: Structured data extraction based on document type
6. **Storage**: Results stored in PostgreSQL and MinIO

## Security

- **Authentication**: JWT-based authentication (to be implemented)
- **Authorization**: Role-based access control
- **Data Encryption**: TLS for data in transit, database encryption for data at rest
- **Privacy**: All processing happens locally - no external API calls
- **Audit Logging**: Comprehensive logging of all operations

## Monitoring

- **Health Checks**: Built-in health check endpoints
- **Logging**: Structured logging with configurable levels
- **Metrics**: Processing time and success rate tracking
- **Error Handling**: Comprehensive error handling and reporting

## Scaling

### Horizontal Scaling
- Multiple API instances behind load balancer
- Separate worker nodes for document processing
- Database clustering for high availability
- Distributed file storage with MinIO clustering

### Performance Optimization
- Async processing with Celery
- Database connection pooling
- File caching and compression
- Background task optimization

## Production Deployment

### Security Checklist
- [ ] Change default passwords and secrets
- [ ] Configure SSL/TLS certificates
- [ ] Set up firewall rules
- [ ] Enable audit logging
- [ ] Configure backup strategies
- [ ] Set up monitoring and alerting

### Environment Variables
- `SECRET_KEY`: Application secret key
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `MINIO_ACCESS_KEY`: MinIO access key
- `MINIO_SECRET_KEY`: MinIO secret key

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

For support and questions:
- Create an issue in the repository
- Check the documentation at `/docs`
- Review the API documentation at `/redoc`
