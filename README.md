# InternSync API

InternSync API provides the backend services for the internship management platform. The API handles user authentication, job postings, applications, and file processing with intelligent resume analysis capabilities.

## What It Does

The API serves as the core backend that powers the InternSync platform:

**User Management:**
- Secure user registration and authentication for students and companies
- JWT token-based session management
- Role-based access control with distinct permissions

**Job Management:**
- Companies can post, edit, and manage internship opportunities
- Students can browse active job listings with filtering
- Automatic pagination for efficient data loading
- Status tracking (draft, active, closed) for job postings

**Application Processing:**
- Students submit applications with resume uploads
- Secure file storage and validation for PDF documents
- Application status management throughout the hiring process
- Real-time tracking of application progress

**File Processing:**
- PDF resume upload and storage
- Text extraction from resumes for AI analysis
- MINIO S3 bucket support
- File size validation and format verification

## Technology Stack

### Core Framework
- **Django 4.2.21** - Python web framework for rapid development
- **Django REST Framework** - RESTful API implementation
- **PostgreSQL** - Production-grade relational database
- **JWT Authentication** - Secure token-based authentication

### File Processing
- **PyPDF2** - PDF text extraction and manipulation
- **pdfplumber** - Advanced PDF parsing capabilities
- **PyMuPDF** - High-performance PDF processing

### Security & Validation
- **Django CORS Headers** - Cross-origin resource sharing configuration
- **Input sanitization** - XSS protection with HTML escaping
- **Password hashing** - Secure password storage with Django's built-in hashers

## Database Schema

The API uses a PostgreSQL database with the following core models:

### Users Table
- **userName** - Unique username for authentication
- **role** - Single character ('s' for student, 'c' for company)
- **password** - Hashed password for secure authentication

### Students Table
- **Fullname** - Student's complete name
- **uid** - Foreign key reference to Users table

### Companies Table (Compony)
- **name** - Company name (unique)
- **hr_mail** - HR contact email address
- **website** - Company website URL
- **uid** - Foreign key reference to Users table

### Jobs Table
- **title** - Job position title
- **description** - Detailed job description
- **short_description** - Brief summary for listings
- **location** - Job location or work arrangement
- **end** - Application deadline
- **status** - Current status (draft, active, closed)
- **work_mode** - Work arrangement (On-Site, Remote, Hybrid)
- **work_type** - Employment type (Full-Time, Part-Time)
- **cid** - Foreign key reference to Companies table

### Applications Table
- **application_date** - Timestamp of application submission
- **status** - Application status (pending, reviewing, shortlisted, etc.)
- **path** - File system path to uploaded resume
- **sid** - Foreign key reference to Students table
- **jid** - Foreign key reference to Jobs table
- **cid** - Foreign key reference to Companies table

## API Endpoints

### Authentication
- `POST /api/user/add` - Register new user (student or company)
- `POST /api/user/login` - Authenticate user and receive JWT token
- `GET /api/user/info` - Verify token validity and get user information

### Job Management
- `POST /api/jobs/add` - Create new job posting (companies only)
- `GET /api/jobs/get` - Retrieve job listings with pagination
- `POST /api/jobs/edit` - Update existing job posting

### Applications
- `POST /api/jobs/apply` - Submit job application with resume
- `GET /api/jobs/get/applications/<job_id>` - Get applicants for specific job
- `GET /api/jobs/get/applications/student` - Get student's application history
- `POST /api/jobs/update/application/status/<application_id>` - Update application status

### File Processing
- `GET /api/jobs/get/applicant/cv/<application_id>` - Download applicant resume
- `GET /api/jobs/extract/pdf/text/<application_id>` - Extract text from resume
- `POST /api/jobs/extract/pdf/text` - Extract text from uploaded PDF

## Getting Started

### Prerequisites
- Python 3.8+ and pip
- PostgreSQL 12+ database server
- Virtual environment (recommended)

### Database Setup

1. Install PostgreSQL and create the database:
```bash
python create_database.py
```
2. rename `mysite/mysite/example.settings.py` to `mysite/mysite/settings.py`

3. 2. rename `mysite/.env.example` to `mysite/.env`

4. Configure database connection in `mysite/.env`:

### S3 setup
Edit S3 config in `mysite/mysite/settings.py`:
```
MINIO_PORT=443
MINIO_USE_SSL=true
MINIO_BUCKET=mybucket
MINIO_REGION=is-sa-eastern-1
MINIO_ENDPOINT=api.s3.dev.is.sa
MINIO_ACCESS_KEY=CHANGE_TO_YOUR_ACCESS_KEY
MINIO_SECRET_KEY=CHANGE_TO_YOUR_SECRET_KEY
```

You can also refer to:
``https://docs.is.sa/doc/how-to-create-s3-bucket-LktU013MBN``

### Installation

1. Navigate to the API directory:
```bash
cd api/internsynk
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run database migrations:
```bash
cd mysite
python manage.py makemigrations
python manage.py migrate
```

5. Start the development server:
```bash
python manage.py runserver
```

The API runs at `http://localhost:8000` and accepts requests from the Angular frontend at `http://localhost:4200`.

## Project Structure

```
api/
├── internsynk/
│   ├── requirements.txt          # Python dependencies
│   └── mysite/                   # Django project
│       ├── manage.py             # Django management script
│       ├── mysite/               # Project settings
│       │   ├── settings.py       # Database and app configuration
│       │   ├── urls.py           # URL routing
│       │   └── wsgi.py           # WSGI application
│       ├── api/                  # Main application
│       │   ├── models.py         # Database models
│       │   ├── serializers.py   # API serializers
│       │   ├── urls.py           # API URL patterns
│       │   ├── admin.py          # Django admin configuration
│       │   ├── views/            # API view controllers
│       │   │   ├── views.py      # User registration and login
│       │   │   ├── post_jobs.py  # Job posting and retrieval
│       │   │   ├── applay.py     # Application submission
│       │   │   ├── get_applications.py  # Application management
│       │   │   ├── edit_jobs.py  # Job editing
│       │   │   ├── pdf_extract.py # Resume text extraction
│       │   │   └── update_application_status.py
│       │   └── migrations/       # Database schema changes
│       ├── files/
│       │   └── cvs/              # Resume file storage
│       └── static/               # Static files and assets
├── create_database.py            # Database setup script
└── README.md
```

## Authentication Flow

The API uses JWT tokens for secure authentication:

1. **Registration**: Users register with role-specific information
2. **Login**: Credentials are verified and JWT token is issued
3. **Authorization**: Each API request includes Bearer token in headers
4. **Token Validation**: Server verifies token signature and expiration
5. **Role-Based Access**: Endpoints check user role for permissions

Token payload includes:
- User ID and username
- Role-specific information (student or company details)
- Token expiration time (1 hour default)

## File Handling

The API processes resume uploads with security measures:

**Upload Process:**
1. Receive base64-encoded PDF from frontend
2. Validate file format using PDF magic number
3. Check file size limits (5MB maximum)
4. Generate unique filename using UUID
5. Store file in S3 bucket
6. Save file path reference in database

**Text Extraction:**
- Multiple PDF parsing libraries for reliability
- Fallback methods ensure text extraction success
- Extracted text feeds AI analysis pipeline

## Security Features

**Data Protection:**
- Input sanitization prevents XSS attacks
- Password hashing with Django's secure hashers
- JWT tokens with configurable expiration
- Database connection uses environment variables

**File Security:**
- File size limits prevent storage abuse
- Unique file naming prevents conflicts
- Secure file storage

**Access Control:**
- Role-based endpoint restrictions
- Token validation on protected routes
- Company-specific data isolation
- Student privacy protection

## Configuration

Key settings in `mysite/mysite/settings.py`:

```python
# Database Configuration
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'internsync',
        'USER': 'postgres',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# JWT Settings
JWT_SECRET = 'your_secret_key'
JWT_ALGORITHM = 'HS256'
JWT_EXP_DELTA_SECONDS = 3600

# CORS Configuration
CORS_ALLOWED_ORIGINS = [
    "http://localhost:4200",  # Angular frontend (that may not work)
]

# File Storage
CV_STORAGE_PATH = "/path/to/resume/storage"

# MINIO S3
MINIO_PORT=443
MINIO_USE_SSL=true
MINIO_BUCKET=mybucket
MINIO_REGION=is-sa-eastern-1
MINIO_ENDPOINT=api.s3.dev.is.sa
MINIO_ACCESS_KEY=CHANGE_TO_YOUR_ACCESS_KEY
MINIO_SECRET_KEY=CHANGE_TO_YOUR_SECRET_KEY
```
 
## Development Notes

The API follows Django best practices with clear separation of concerns:

- **Models** define database structure and relationships
- **Serializers** handle data validation and JSON conversion
- **Views** implement business logic and HTTP response handling
- **URLs** provide clean RESTful endpoint structure

Database migrations track all schema changes, ensuring consistent development and production environments. The PostgreSQL database provides reliable transaction support and efficient querying for the application's needs.

File processing includes multiple PDF parsing libraries to handle various resume formats. The base64 encoding ensures secure file transmission between frontend and backend systems.

## Authors

**Mustafa Al-Jishi**  
Cybersecurity and Digital Forensics Student, IAU  
 
**Mohammed Al-Mutawah**  
Cybersecurity and Digital Forensics Student, IAU 

made in Innosoft
