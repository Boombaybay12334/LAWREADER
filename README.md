# Legal Document Analyzer

A comprehensive web application for legal document analysis and query processing, built with FastAPI backend and React frontend.

## Features

### 🔍 PDF Document Analyzer
- Upload and analyze legal documents
- Automated document processing
- Secure file handling with automatic cleanup
- Progress tracking and error handling
- Download processed documents

### 💬 Legal Query System
- Ask complex legal questions
- Get detailed, researched answers
- Query history tracking
- Professional legal knowledge base
- Real-time response processing

### 🎨 Professional Interface
- Modern, responsive design
- Intuitive navigation
- Real-time feedback
- Error handling and success notifications
- Professional color scheme optimized for legal professionals

## Tech Stack

### Backend
- **FastAPI** - High-performance Python web framework
- **Uvicorn** - ASGI server for production
- **Pydantic** - Data validation and settings management
- **Python Multipart** - File upload handling
- **CORS** - Cross-origin resource sharing

### Frontend
- **React 18** - Modern React with hooks
- **TypeScript** - Type-safe JavaScript
- **Tailwind CSS** - Utility-first CSS framework
- **React Router** - Client-side routing
- **Axios** - HTTP client for API calls
- **Lucide React** - Beautiful icons

## Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- npm or yarn

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create necessary directories:
```bash
mkdir uploads processed
```

5. Start the server:
```bash
python main.py
```

The API will be available at `http://localhost:8000`

### Frontend Setup

1. Install dependencies:
```bash
npm install
```

2. Install additional required packages:
```bash
npm install react-router-dom axios
```

3. Start the development server:
```bash
npm run dev
```

The application will be available at `http://localhost:5173`

## API Endpoints

### Health Check
- `GET /health` - Server health status

### PDF Analysis
- `POST /upload-pdf` - Upload and analyze PDF documents
- `GET /download/{file_id}` - Download processed documents

### Legal Queries
- `POST /legal-query` - Process legal questions

## Project Structure

```
legal-document-analyzer/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── requirements.txt     # Python dependencies
│   ├── .env                 # Environment variables
│   ├── uploads/             # Temporary upload directory
│   └── processed/           # Processed files directory
├── src/
│   ├── components/          # React components
│   │   ├── Layout.tsx
│   │   ├── LoadingSpinner.tsx
│   │   ├── ErrorMessage.tsx
│   │   └── SuccessMessage.tsx
│   ├── pages/              # Page components
│   │   ├── Home.tsx
│   │   ├── PDFAnalyzer.tsx
│   │   └── LegalQuery.tsx
│   ├── services/           # API services
│   │   └── api.ts
│   ├── types/              # TypeScript types
│   │   └── index.ts
│   └── App.tsx             # Main application component
├── package.json
└── README.md
```

## Configuration

### Environment Variables (Backend)
Create a `.env` file in the backend directory:

```env
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=True
LOG_LEVEL=INFO
MAX_FILE_SIZE=10485760
UPLOAD_DIR=uploads
PROCESSED_DIR=processed
```

### Security Features
- File type validation (PDF only)
- File size limits (10MB maximum)
- Automatic file cleanup (files older than 1 hour)
- CORS configuration for frontend integration
- Input sanitization and validation

## Tool Integration

### Tool 1: PDF Document Analyzer
Replace the simulation code in `main.py` with actual tool execution:

```python
# Replace the simulation with:
result = subprocess.run([
    "python", "-m", "pipeline.main", "--file", str(input_path)
], capture_output=True, text=True, timeout=300)
```

### Tool 2: Legal Query System
Replace the simulation code in `main.py` with actual tool execution:

```python
# Replace the simulation with:
result = subprocess.run([
    "python", "lawreader_main.py", "-q", query.question
], capture_output=True, text=True, timeout=120)
```

## Development

### Running Tests
```bash
# Backend tests (if implemented)
cd backend
python -m pytest

# Frontend tests
npm test
```

### Building for Production
```bash
# Build frontend
npm run build

# Start production server
npm run preview
```

## Deployment

### Backend Deployment
```bash
# Using uvicorn directly
uvicorn main:app --host 0.0.0.0 --port 8000

# Using gunicorn for production
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Frontend Deployment
```bash
npm run build
# Deploy the dist/ directory to your hosting service
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License.

## Support

For support and questions, please create an issue in the repository.