# Real Estate Caller Agent - Backend API

An AI-powered real estate calling platform that automates prospect outreach using intelligent voice agents. This backend API manages campaigns, prospects, documents, and call interactions.

## Overview

This is a FastAPI-based backend service for a Real Estate Caller Agent system. It provides comprehensive APIs for:
- User authentication and management
- Project management
- Campaign creation and management
- Prospect management (bulk upload, updates)
- Document processing and extraction
- Call orchestration and logging
- Voice agent configuration
- Analytics and dashboard statistics

## Tech Stack

- **Framework**: FastAPI 0.135.1+
- **Database**: PostgreSQL with SQLModel ORM
- **Authentication**: JWT with Passlib/BCrypt
- **Voice Service**: ElevenLabs integration
- **Document Processing**: PyPDF2, PyMuPDF, Tesseract OCR, python-docx
- **Server**: Uvicorn
- **Container**: Docker & Docker Compose

## Prerequisites

- Python 3.12+
- PostgreSQL Database
- Redis (for caching)
- OpenAI API key
- ElevenLabs API key

## Project Structure

```
Backend/
├── src/
│   └── app/
│       ├── auth/              # Authentication & authorization
│       ├── calls/             # Call management & recording
│       ├── campaigns/         # Campaign CRUD & management
│       ├── common/            # Shared utilities & settings
│       ├── dashboard/         # Analytics & statistics
│       ├── database/          # SQLModel & database config
│       ├── documents/         # Document processing
│       ├── projects/          # Project management
│       ├── prospects/         # Prospect management
│       ├── services/          # External service integrations
│       └── v1/                # API v1 routes & models
├── config.yml                 # Configuration file
├── main.py                    # Application entry point
├── pyproject.toml            # Project dependencies
└── docker-compose.yml        # Docker setup
```

## Installation

### Local Development

1. **Clone the repository** and navigate to the Backend directory:
   ```bash
   cd Backend
   ```

2. **Install dependencies**:
   ```bash
   pip install -e .
   ```

3. **Configure environment**:
   - Copy `config.yml` and update with your values:
     - `DB_TYPE`: postgresql
     - `APP_NAME`: RealEstate Caller
     - `UPLOAD_DIR`: ./uploads

4. **Set up environment variables**:
   ```bash
   # Create a .env file with:
   DATABASE_URL=postgresql://user:password@localhost:5432/realestatedb
   JWT_SECRET=your_secret_key_here
   OPENAI_API_KEY=your_openai_key
   ELEVENLABS_API_KEY=your_elevenlabs_key
   ```

5. **Initialize database**:
   ```bash
   alembic upgrade head
   ```

6. **Run the application**:
   ```bash
   python main.py
   ```

   The API will be available at `http://localhost:8000`

### Docker Deployment

1. **Build and run with Docker Compose**:
   ```bash
   docker-compose up --build
   ```

2. **Access the API**:
   - API: http://localhost:8000
   - Swagger Docs: http://localhost:8000/api/docs
   - ReDoc: http://localhost:8000/api/redoc

## API Documentation

### Base URL
```
/api/v1
```

### Authentication Endpoints

#### POST `/auth/register`
Register a new user account.

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "secure_password",
  "name": "User Name"
}
```

**Response**: User object with JWT token

---

#### POST `/auth/login`
User login.

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "password"
}
```

**Response**:
```json
{
  "access_token": "jwt_token",
  "token_type": "bearer"
}
```

---

#### GET `/auth/me`
Get current authenticated user profile.

**Response**: User object

---

#### PUT `/auth/me`
Update current user profile.

**Request Body**:
```json
{
  "name": "Updated Name",
  "email": "newemail@example.com"
}
```

**Response**: Updated user object

---

### Projects Endpoints

#### POST `/projects`
Create a new project.

**Request Body**:
```json
{
  "name": "Project Name",
  "description": "Project Description"
}
```

**Response**: Project object

---

#### GET `/projects`
List all projects for the user.

**Response**: Array of project objects

---

#### GET `/projects/{project_id}`
Get specific project details.

**Response**: Project object

---

#### PUT `/projects/{project_id}`
Update project information.

**Request Body**:
```json
{
  "name": "Updated Name",
  "description": "Updated Description"
}
```

**Response**: Updated project object

---

#### DELETE `/projects/{project_id}`
Delete a project.

**Response**: Success message

---

### Campaigns Endpoints

#### POST `/campaigns`
Create a new campaign.

**Request Body**:
```json
{
  "name": "Campaign Name",
  "project_id": 1,
  "description": "Campaign Description",
  "agent_config": {},
  "voice_id": "voice_id"
}
```

**Response**: Campaign object

---

#### GET `/campaigns`
List campaigns (optionally filtered by project).

**Query Parameters**:
- `project_id` (optional): Filter by project ID

**Response**: Array of campaign objects

---

#### GET `/campaigns/{campaign_id}`
Get campaign details.

**Response**: Campaign object with statistics

---

#### PUT `/campaigns/{campaign_id}`
Update campaign settings.

**Response**: Updated campaign object

---

#### DELETE `/campaigns/{campaign_id}`
Delete a campaign.

**Response**: Success message

---

#### POST `/campaigns/{campaign_id}/activate`
Activate a campaign.

**Response**: Updated campaign object

---

#### POST `/campaigns/{campaign_id}/pause`
Pause an active campaign.

**Response**: Updated campaign object

---

#### GET `/campaigns/{campaign_id}/agent`
Get campaign agent details.

**Response**: Agent configuration and details

---

#### POST `/campaigns/{campaign_id}/regenerate-agent`
Regenerate the campaign's AI agent.

**Response**: Updated agent configuration

---

### Prospects Endpoints

#### POST `/prospects`
Add a single prospect.

**Request Body**:
```json
{
  "name": "Prospect Name",
  "phone": "+1234567890",
  "email": "prospect@example.com",
  "project_id": 1,
  "metadata": {}
}
```

**Response**: Prospect object

---

#### POST `/prospects/bulk-upload`
Bulk upload prospects via CSV/Excel.

**Request**: Multipart form with file upload

**Response**: Upload status and created prospect count

---

#### GET `/prospects`
List prospects for a project.

**Query Parameters**:
- `project_id` (required): Project ID to fetch prospects for
- `skip` (optional): Pagination skip (default: 0)
- `limit` (optional): Pagination limit (default: 100)

**Response**: Array of prospect objects

---

#### GET `/prospects/{prospect_id}`
Get prospect details.

**Response**: Prospect object with call history

---

#### PUT `/prospects/{prospect_id}`
Update prospect information.

**Request Body**:
```json
{
  "name": "Updated Name",
  "email": "newemail@example.com",
  "metadata": {}
}
```

**Response**: Updated prospect object

---

#### DELETE `/prospects/{prospect_id}`
Delete a prospect.

**Response**: Success message

---

### Calls Endpoints

#### POST `/calls/make-call`
Initiate a single call to a prospect.

**Request Body**:
```json
{
  "prospect_id": 1,
  "campaign_id": 1
}
```

**Response**: Call object with call ID and timestamp

---

#### POST `/calls/start-campaign`
Start automated campaign calls.

**Request Body**:
```json
{
  "campaign_id": 1,
  "batch_size": 10
}
```

**Response**: Campaign execution status

---

#### GET `/calls/logs`
Get call logs and history.

**Query Parameters**:
- `campaign_id` (optional): Filter by campaign
- `status` (optional): Filter by call status (completed, failed, pending)
- `skip` (optional): Pagination skip
- `limit` (optional): Pagination limit

**Response**: Array of call logs

---

#### GET `/calls/{conversation_id}/audio`
Retrieve call audio recording.

**Response**: Audio file stream

---

#### GET `/calls/{conversation_id}/chat`
Retrieve conversation transcript.

**Response**: Conversation messages and transcript

---

#### PUT `/calls/{call_id}/outcome`
Update call outcome and disposition.

**Request Body**:
```json
{
  "outcome": "interested|not_interested|callback_requested",
  "notes": "Additional notes"
}
```

**Response**: Updated call object

---

#### POST `/calls/refresh-outcomes`
Refresh all call outcomes from external system.

**Response**: Refresh status

---

#### GET `/calls/hot-prospects`
Get list of hot/interested prospects.

**Response**: Array of qualified prospect objects

---

#### GET `/campaigns/{campaign_id}/stats`
Get campaign call statistics.

**Response**:
```json
{
  "total_calls": 100,
  "completed_calls": 85,
  "failed_calls": 5,
  "interested_prospects": 15,
  "callback_requested": 10,
  "success_rate": 85.0
}
```

---

#### GET `/calls/voices/list`
List available ElevenLabs voices.

**Response**: Array of available voice configurations

---

### Documents Endpoints

#### POST `/documents/upload`
Upload and process a document.

**Request**: Multipart form with file upload

**Response**: Document object with extracted text

---

#### GET `/documents`
List all documents in a project.

**Query Parameters**:
- `project_id` (required): Project ID

**Response**: Array of document objects

---

#### GET `/documents/{document_id}`
Get document details.

**Response**: Document metadata and extracted content

---

#### GET `/documents/{document_id}/text`
Get extracted text from document.

**Response**: Plain text content

---

#### POST `/documents/{document_id}/reprocess`
Reprocess a document (e.g., re-extract text with updated OCR).

**Response**: Updated document with new extracted content

---

#### DELETE `/documents/{document_id}`
Delete a document.

**Response**: Success message

---

### Dashboard Endpoints

#### GET `/dashboard/stats`
Get overall dashboard statistics.

**Response**:
```json
{
  "total_projects": 5,
  "total_campaigns": 15,
  "total_prospects": 500,
  "total_calls": 1200,
  "success_rate": 42.0,
  "hot_prospects": 150,
  "pending_calls": 50
}
```

---

## Authentication

The API uses JWT (JSON Web Tokens) for authentication. Include the token in the Authorization header:

```
Authorization: Bearer <your_jwt_token>
```

## Error Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 409 | Conflict |
| 500 | Internal Server Error |

## Development

### Running Tests

```bash
pytest tests/
```

### Code Style

The project follows PEP 8 standards. Format code with:

```bash
black src/
```

### Logging

Logging is configured in `logging.json`. Logs are output to:
- Console (DEBUG level in development)
- File: `logs/app.log`

## Troubleshooting

### Database Connection Issues

- Ensure PostgreSQL is running
- Verify `DATABASE_URL` environment variable
- Check database credentials in `config.yml`

### Missing Dependencies

```bash
pip install -e . --upgrade
```

### Port Already in Use

Change the port in `main.py`:
```python
uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
```

## Performance Optimization

- Database queries are optimized with proper indexing
- Redis caching for frequently accessed data
- Batch processing for bulk operations
- Async endpoints for I/O operations

## Security Considerations

- All passwords are hashed with BCrypt
- JWT tokens expire after configured duration
- CORS enabled for frontend integration
- SQL injection prevention through SQLModel ORM
- Input validation via Pydantic models

## Deployment

### Production Checklist

- [ ] Set `reload=False` in production
- [ ] Configure proper JWT secret
- [ ] Set up HTTPS/SSL
- [ ] Configure database backups
- [ ] Set up monitoring and logging aggregation
- [ ] Configure rate limiting
- [ ] Use environment variables for secrets

## Support & Documentation

- **Swagger UI**: `/api/docs`
- **ReDoc**: `/api/redoc`
- **Issues**: Report via GitHub Issues
- **API Status**: `/health`

## License

Proprietary - All Rights Reserved

## Related Documentation

- [API Documentation](./API_DOCUMENTATION.md)
- [Docker Setup](./docker-compose.yml)
- [Configuration](./config.yml)
