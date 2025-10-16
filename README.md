# 🚀 Quick Start Guide - Document Parser

Get your Document Parser up and running in minutes with real document content extraction!

## Prerequisites

- **Python 3.11+**
- **Git**

## Installation Steps

### 1. Setup Environment

```bash
# Clone the repository (if not already done)
git clone https://github.com/shreyescodes/doc_parser_updated/
cd doc-parser

# Create virtual environment (recommended)
python -m venv myenv
myenv\Scripts\activate  # Windows
# source myenv/bin/activate  # Linux/Mac

# Install core dependencies
pip install fastapi uvicorn python-multipart pydantic pydantic-settings PyPDF2
```

### 2. Start the Simple Application

```bash
# Run the enhanced document parser
python simple_app.py
```

**✅ The application will start at http://localhost:8000**

### 3. Access the Application

- **API Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

**🎉 No authentication required for testing!**

## 🚀 Quick Document Processing

### Supported File Formats
- **PDF Files** (`.pdf`) - Full text extraction and parsing
- **Text Files** (`.txt`) - Direct text processing

### Document Processing Commands

```bash
# Option 1: Upload and process in one step (Recommended)
curl -X POST "http://localhost:8000/process-file" \
     -F "file=@your_document.pdf"

# Option 2: Upload first, then process
curl -X POST "http://localhost:8000/upload" \
     -F "file=@your_document.pdf"

# Then process (use document_id from upload response)
curl -X POST "http://localhost:8000/process/doc_20251016_043214?filename=your_document.pdf"

# List all uploaded documents
curl -X GET "http://localhost:8000/documents"

# Get specific document details
curl -X GET "http://localhost:8000/documents/doc_20251016_043214"
```

### Development Commands

```bash
# Run with auto-reload
python simple_app.py

# Install additional dependencies if needed
pip install -r requirements.txt
```

## 📊 What Gets Extracted

Your document parser extracts **real information** from documents:

### Extracted Data Types
- **Contact Information**: Names, emails, phone numbers
- **Dates**: Birth dates, employment dates, education dates  
- **Skills**: Programming languages, technologies, tools
- **Education**: Degrees, universities, certifications
- **Experience**: Job titles, companies, work history
- **Financial Data**: Dollar amounts, percentages
- **Addresses**: Street addresses, locations
- **Document Classification**: Resume, invoice, contract, report

### Example JSON Response

```json
{
  "document_id": "doc_20251016_043214",
  "filename": "resume.pdf",
  "file_size": 123456,
  "extracted_data": {
    "file_info": {
      "filename": "resume.pdf",
      "file_type": ".pdf",
      "processed_at": "2025-10-16T04:32:14"
    },
    "extracted_text": "John Doe\nSoftware Engineer\nEmail: john@example.com...",
    "document_type": "resume",
    "confidence": 0.9,
    "structured_data": {
      "contact_info": {"name": "John Doe"},
      "emails": ["john@example.com"],
      "phones": ["(555) 123-4567"],
      "skills": ["Python", "JavaScript", "React", "AWS"],
      "education": ["Bachelor of Computer Science"],
      "experience": ["Software Engineer at Tech Corp"]
    }
  },
  "processing_status": "completed"
}
```

## Troubleshooting

### Common Issues

#### Missing Dependencies
```bash
# Install core dependencies
pip install fastapi uvicorn python-multipart pydantic pydantic-settings PyPDF2

# If you get compilation errors, try pre-compiled wheels
pip install --only-binary=all PyPDF2
```

#### Port Already in Use
```bash
# Kill process on port 8000 (Windows)
netstat -ano | findstr :8000
taskkill /PID <PID_NUMBER> /F

# Kill process on port 8000 (Linux/Mac)
lsof -ti:8000 | xargs kill -9

# Or use different port
python simple_app.py  # Edit the port in the file
```

#### File Upload Issues
```bash
# Check if uploads directory exists
mkdir uploads

# Ensure file permissions
chmod 755 uploads/  # Linux/Mac
```

#### PDF Processing Errors
```bash
# If PDF processing fails, try with a simple text file first
echo "Test document content" > test.txt
curl -X POST "http://localhost:8000/process-file" -F "file=@test.txt"
```

## 🎯 Quick Test

### Test with Your Resume

1. **Start the application:**
   ```bash
   python simple_app.py
   ```

2. **Upload your resume:**
   ```bash
   curl -X POST "http://localhost:8000/process-file" \
        -F "file=@your_resume.pdf"
   ```

3. **View results** in the JSON response or visit `http://localhost:8000/docs` for interactive testing!

## 📈 Features

### ✅ What's Working
- **Real PDF text extraction** using PyPDF2
- **Structured data parsing** (emails, phones, skills, etc.)
- **Document classification** (resume, invoice, contract, report)
- **JSON API responses** with extracted information
- **No authentication required** for testing
- **Interactive API documentation** at `/docs`

### 🔧 Easy to Extend
- Add new document types
- Customize extraction patterns
- Add more file format support
- Integrate with databases
- Add authentication

## 🚀 Production Ready Features

For production deployment, you can enhance the simple app with:

### Database Integration
```python
# Add to simple_app.py
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True)
    filename = Column(String(255))
    extracted_data = Column(Text)
```

### Authentication
```python
# Add JWT authentication
from fastapi.security import HTTPBearer
from jose import JWTError, jwt

security = HTTPBearer()

@app.post("/upload")
async def upload_document(file: UploadFile = File(...), token: str = Depends(security)):
    # Verify token and process
```

### Advanced Processing
```python
# Add OCR support
import pytesseract
from PIL import Image

def extract_text_from_image(image_path):
    return pytesseract.image_to_string(Image.open(image_path))
```

## 📚 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API information |
| `/health` | GET | Health check |
| `/upload` | POST | Upload document |
| `/process/{doc_id}` | POST | Process uploaded document |
| `/process-file` | POST | Upload and process in one step |
| `/documents` | GET | List all documents |
| `/documents/{doc_id}` | GET | Get document details |
| `/docs` | GET | Interactive API documentation |

## 🎉 Ready to Use!

Your document parser is now ready to extract real information from PDFs and text files. Start with `python simple_app.py` and test with your documents!

**Happy Document Parsing!** 📄✨
