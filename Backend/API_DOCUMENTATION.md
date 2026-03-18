# Real Estate Caller Agent - API Documentation

**API Version**: 1.0.0  
**Base URL**: `http://localhost:8000/api/v1`  
**Authentication**: JWT Bearer Token

---

## Table of Contents

1. [Overview](#overview)
2. [Authentication](#authentication)
3. [Response Format](#response-format)
4. [Error Handling](#error-handling)
5. [Authentication Endpoints](#authentication-endpoints)
6. [Projects Endpoints](#projects-endpoints)
7. [Campaigns Endpoints](#campaigns-endpoints)
8. [Prospects Endpoints](#prospects-endpoints)
9. [Calls Endpoints](#calls-endpoints)
10. [Documents Endpoints](#documents-endpoints)
11. [Dashboard Endpoints](#dashboard-endpoints)
12. [Data Models](#data-models)

---

## Overview

The Real Estate Caller Agent API is a comprehensive platform for managing AI-powered calling campaigns for real estate prospecting. The API provides full-featured endpoints for:

- **User Management**: Registration, authentication, profile updates
- **Project Management**: Create and manage real estate projects
- **Campaign Management**: Configure and control calling campaigns
- **Prospect Management**: Add, update, and manage prospect lists
- **Call Management**: Initiate calls, manage outcomes, retrieve recordings
- **Document Processing**: Upload and extract information from documents
- **Analytics**: Dashboard statistics and campaign performance metrics

---

## Authentication

### Overview

The API uses JWT (JSON Web Tokens) for authentication. All endpoints except `/auth/register` and `/auth/login` require a valid JWT token.

### Token Usage

Include the token in the `Authorization` header:

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Token Expiration

Tokens expire after a configured duration (default: 24 hours). Use the `/auth/login` endpoint to obtain a new token when expired.

### Security Best Practices

- Store tokens securely (never expose in URLs or logs)
- Use HTTPS in production
- Refresh tokens before expiration
- Logout by discarding the token client-side

---

## Response Format

### Success Response

All successful responses follow this format:

```json
{
  "data": {
    // Response payload
  },
  "status": "success",
  "timestamp": "2024-03-12T10:30:00Z"
}
```

Or for list endpoints:

```json
{
  "data": [
    // Array of items
  ],
  "total": 100,
  "skip": 0,
  "limit": 50,
  "status": "success"
}
```

### Error Response

```json
{
  "detail": "Error message describing what went wrong",
  "status": "error",
  "error_code": "SPECIFIC_ERROR_CODE"
}
```

---

## Error Handling

### HTTP Status Codes

| Status | Description |
|--------|-------------|
| 200 | OK - Request succeeded |
| 201 | Created - Resource created successfully |
| 400 | Bad Request - Invalid input parameters |
| 401 | Unauthorized - Missing or invalid token |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found - Resource not found |
| 409 | Conflict - Resource already exists |
| 422 | Unprocessable Entity - Validation error |
| 500 | Internal Server Error - Server-side error |

### Common Error Codes

| Code | Description |
|------|-------------|
| `INVALID_CREDENTIALS` | Invalid email or password |
| `USER_ALREADY_EXISTS` | Email already registered |
| `UNAUTHORIZED` | JWT token missing or invalid |
| `RESOURCE_NOT_FOUND` | Requested resource doesn't exist |
| `VALIDATION_ERROR` | Input validation failed |
| `DATABASE_ERROR` | Database operation failed |

### Error Response Example

```json
{
  "detail": "Invalid email or password",
  "status": "error",
  "error_code": "INVALID_CREDENTIALS"
}
```

---

## Authentication Endpoints

### POST /auth/register

Register a new user account.

**Request Body**:
```json
{
  "email": "john@example.com",
  "password": "SecurePass123!",
  "name": "John Doe"
}
```

**Parameters**:
- `email` (string, required): User's email address
- `password` (string, required): Password (min 8 characters)
- `name` (string, required): User's full name

**Response** (201 Created):
```json
{
  "id": 1,
  "email": "john@example.com",
  "name": "John Doe",
  "created_at": "2024-03-12T10:30:00Z"
}
```

**Errors**:
- 400: Invalid email format
- 409: Email already registered

---

### POST /auth/login

Authenticate user and receive JWT token.

**Request Body**:
```json
{
  "email": "john@example.com",
  "password": "SecurePass123!"
}
```

**Parameters**:
- `email` (string, required): User's email
- `password` (string, required): User's password

**Response** (200 OK):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIn0...",
  "token_type": "bearer",
  "expires_in": 86400
}
```

**Errors**:
- 400: Invalid email or password
- 401: Account inactive

---

### GET /auth/me

Get current authenticated user's profile.

**Headers**:
```
Authorization: Bearer <token>
```

**Response** (200 OK):
```json
{
  "id": 1,
  "email": "john@example.com",
  "name": "John Doe",
  "created_at": "2024-03-12T10:30:00Z",
  "updated_at": "2024-03-12T10:30:00Z"
}
```

**Errors**:
- 401: Unauthorized (missing or invalid token)

---

### PUT /auth/me

Update current user's profile information.

**Headers**:
```
Authorization: Bearer <token>
```

**Request Body**:
```json
{
  "name": "John Smith",
  "email": "john.smith@example.com"
}
```

**Parameters** (all optional):
- `name` (string): Updated name
- `email` (string): Updated email

**Response** (200 OK):
```json
{
  "id": 1,
  "email": "john.smith@example.com",
  "name": "John Smith",
  "updated_at": "2024-03-12T11:00:00Z"
}
```

**Errors**:
- 401: Unauthorized
- 409: Email already in use

---

## Projects Endpoints

### POST /projects

Create a new project.

**Headers**:
```
Authorization: Bearer <token>
```

**Request Body**:
```json
{
  "name": "Downtown Residential Development",
  "description": "Marketing campaign for downtown properties"
}
```

**Parameters**:
- `name` (string, required): Project name
- `description` (string, optional): Project description

**Response** (201 Created):
```json
{
  "id": 1,
  "name": "Downtown Residential Development",
  "description": "Marketing campaign for downtown properties",
  "user_id": 1,
  "created_at": "2024-03-12T10:30:00Z"
}
```

---

### GET /projects

List all projects for the current user.

**Headers**:
```
Authorization: Bearer <token>
```

**Query Parameters**:
- `skip` (integer, optional): Pagination offset (default: 0)
- `limit` (integer, optional): Pagination limit (default: 100)

**Response** (200 OK):
```json
{
  "data": [
    {
      "id": 1,
      "name": "Downtown Residential Development",
      "description": "Marketing campaign for downtown properties",
      "user_id": 1,
      "created_at": "2024-03-12T10:30:00Z"
    }
  ],
  "total": 5,
  "skip": 0,
  "limit": 100
}
```

---

### GET /projects/{project_id}

Get details of a specific project.

**Headers**:
```
Authorization: Bearer <token>
```

**Path Parameters**:
- `project_id` (integer): Project ID

**Response** (200 OK):
```json
{
  "id": 1,
  "name": "Downtown Residential Development",
  "description": "Marketing campaign for downtown properties",
  "user_id": 1,
  "campaign_count": 3,
  "prospect_count": 250,
  "created_at": "2024-03-12T10:30:00Z"
}
```

**Errors**:
- 404: Project not found

---

### PUT /projects/{project_id}

Update project information.

**Headers**:
```
Authorization: Bearer <token>
```

**Path Parameters**:
- `project_id` (integer): Project ID

**Request Body**:
```json
{
  "name": "Updated Project Name",
  "description": "Updated description"
}
```

**Response** (200 OK):
```json
{
  "id": 1,
  "name": "Updated Project Name",
  "description": "Updated description",
  "updated_at": "2024-03-12T11:00:00Z"
}
```

**Errors**:
- 404: Project not found

---

### DELETE /projects/{project_id}

Delete a project and all associated campaigns and prospects.

**Headers**:
```
Authorization: Bearer <token>
```

**Path Parameters**:
- `project_id` (integer): Project ID

**Response** (200 OK):
```json
{
  "message": "Project deleted successfully"
}
```

**Errors**:
- 404: Project not found

---

## Campaigns Endpoints

### POST /campaigns

Create a new campaign.

**Headers**:
```
Authorization: Bearer <token>
```

**Request Body**:
```json
{
  "name": "Spring Listing Campaign",
  "project_id": 1,
  "description": "Marketing campaign for spring listings",
  "voice_id": "EXAVITQu4vr4xnSDxMaL",
  "agent_prompt": "You are a friendly real estate agent..."
}
```

**Parameters**:
- `name` (string, required): Campaign name
- `project_id` (integer, required): Associated project ID
- `description` (string, optional): Campaign description
- `voice_id` (string, required): ElevenLabs voice ID
- `agent_prompt` (string, required): AI agent system prompt

**Response** (201 Created):
```json
{
  "id": 1,
  "name": "Spring Listing Campaign",
  "project_id": 1,
  "description": "Marketing campaign for spring listings",
  "status": "inactive",
  "created_at": "2024-03-12T10:30:00Z"
}
```

---

### GET /campaigns

List campaigns for the current user.

**Headers**:
```
Authorization: Bearer <token>
```

**Query Parameters**:
- `project_id` (integer, optional): Filter by project ID
- `status` (string, optional): Filter by status (active, inactive, paused)
- `skip` (integer, optional): Pagination offset
- `limit` (integer, optional): Pagination limit

**Response** (200 OK):
```json
{
  "data": [
    {
      "id": 1,
      "name": "Spring Listing Campaign",
      "project_id": 1,
      "status": "active",
      "total_prospects": 100,
      "completed_calls": 85,
      "created_at": "2024-03-12T10:30:00Z"
    }
  ],
  "total": 5,
  "skip": 0,
  "limit": 100
}
```

---

### GET /campaigns/{campaign_id}

Get campaign details with statistics.

**Headers**:
```
Authorization: Bearer <token>
```

**Path Parameters**:
- `campaign_id` (integer): Campaign ID

**Response** (200 OK):
```json
{
  "id": 1,
  "name": "Spring Listing Campaign",
  "project_id": 1,
  "description": "Marketing campaign for spring listings",
  "status": "active",
  "voice_id": "EXAVITQu4vr4xnSDxMaL",
  "total_prospects": 100,
  "completed_calls": 85,
  "successful_calls": 42,
  "failed_calls": 5,
  "interested_prospects": 15,
  "callback_requested": 10,
  "success_rate": 49.4,
  "created_at": "2024-03-12T10:30:00Z"
}
```

---

### PUT /campaigns/{campaign_id}

Update campaign settings.

**Headers**:
```
Authorization: Bearer <token>
```

**Path Parameters**:
- `campaign_id` (integer): Campaign ID

**Request Body**:
```json
{
  "name": "Updated Campaign Name",
  "description": "Updated description",
  "agent_prompt": "Updated prompt..."
}
```

**Response** (200 OK):
```json
{
  "id": 1,
  "name": "Updated Campaign Name",
  "description": "Updated description",
  "updated_at": "2024-03-12T11:00:00Z"
}
```

---

### DELETE /campaigns/{campaign_id}

Delete a campaign.

**Headers**:
```
Authorization: Bearer <token>
```

**Path Parameters**:
- `campaign_id` (integer): Campaign ID

**Response** (200 OK):
```json
{
  "message": "Campaign deleted successfully"
}
```

**Errors**:
- 404: Campaign not found

---

### POST /campaigns/{campaign_id}/activate

Activate a campaign to start making calls.

**Headers**:
```
Authorization: Bearer <token>
```

**Path Parameters**:
- `campaign_id` (integer): Campaign ID

**Response** (200 OK):
```json
{
  "id": 1,
  "status": "active",
  "activated_at": "2024-03-12T11:00:00Z",
  "message": "Campaign activated successfully"
}
```

---

### POST /campaigns/{campaign_id}/pause

Pause an active campaign.

**Headers**:
```
Authorization: Bearer <token>
```

**Path Parameters**:
- `campaign_id` (integer): Campaign ID

**Response** (200 OK):
```json
{
  "id": 1,
  "status": "paused",
  "paused_at": "2024-03-12T11:00:00Z",
  "message": "Campaign paused successfully"
}
```

---

### GET /campaigns/{campaign_id}/agent

Get campaign AI agent configuration details.

**Headers**:
```
Authorization: Bearer <token>
```

**Path Parameters**:
- `campaign_id` (integer): Campaign ID

**Response** (200 OK):
```json
{
  "agent_id": "agent_xyz123",
  "name": "Spring Campaign Agent",
  "voice_id": "EXAVITQu4vr4xnSDxMaL",
  "model": "gpt-4",
  "system_prompt": "You are a friendly real estate agent...",
  "status": "active",
  "created_at": "2024-03-12T10:30:00Z"
}
```

---

### POST /campaigns/{campaign_id}/regenerate-agent

Regenerate the AI agent for a campaign.

**Headers**:
```
Authorization: Bearer <token>
```

**Path Parameters**:
- `campaign_id` (integer): Campaign ID

**Response** (200 OK):
```json
{
  "agent_id": "agent_xyz123_v2",
  "message": "Agent regenerated successfully",
  "regenerated_at": "2024-03-12T11:00:00Z"
}
```

---

### GET /campaigns/{campaign_id}/stats

Get detailed campaign statistics.

**Headers**:
```
Authorization: Bearer <token>
```

**Path Parameters**:
- `campaign_id` (integer): Campaign ID

**Response** (200 OK):
```json
{
  "total_prospects": 100,
  "completed_calls": 85,
  "failed_calls": 5,
  "pending_calls": 10,
  "interested_prospects": 15,
  "callback_requested": 10,
  "not_interested": 60,
  "success_rate": 49.4,
  "avg_call_duration": 245,
  "total_call_duration": 20825,
  "campaign_id": 1,
  "campaign_name": "Spring Listing Campaign"
}
```

---

## Prospects Endpoints

### POST /prospects

Add a single prospect to a project.

**Headers**:
```
Authorization: Bearer <token>
```

**Request Body**:
```json
{
  "name": "Jane Smith",
  "phone": "+1-555-123-4567",
  "email": "jane.smith@example.com",
  "project_id": 1,
  "metadata": {
    "property_type": "residential",
    "zip_code": "90210"
  }
}
```

**Parameters**:
- `name` (string, required): Prospect name
- `phone` (string, required): Phone number
- `email` (string, required): Email address
- `project_id` (integer, required): Associated project ID
- `metadata` (object, optional): Custom metadata

**Response** (201 Created):
```json
{
  "id": 1,
  "name": "Jane Smith",
  "phone": "+1-555-123-4567",
  "email": "jane.smith@example.com",
  "project_id": 1,
  "metadata": {
    "property_type": "residential",
    "zip_code": "90210"
  },
  "created_at": "2024-03-12T10:30:00Z"
}
```

---

### POST /prospects/bulk-upload

Upload multiple prospects from a file (CSV/Excel).

**Headers**:
```
Authorization: Bearer <token>
Content-Type: multipart/form-data
```

**Form Parameters**:
- `file` (file, required): CSV or Excel file
- `project_id` (integer, required): Project ID

**File Format** (CSV):
```csv
name,phone,email,property_type,zip_code
Jane Smith,+1-555-123-4567,jane@example.com,residential,90210
John Doe,+1-555-234-5678,john@example.com,commercial,90211
```

**Response** (200 OK):
```json
{
  "total_uploaded": 150,
  "successful": 148,
  "failed": 2,
  "errors": [
    {
      "row": 5,
      "error": "Invalid phone number format"
    }
  ],
  "message": "Bulk upload completed"
}
```

---

### GET /prospects

List prospects for a project.

**Headers**:
```
Authorization: Bearer <token>
```

**Query Parameters**:
- `project_id` (integer, required): Project ID to filter by
- `status` (string, optional): Filter by status (new, called, interested, not_interested)
- `skip` (integer, optional): Pagination offset
- `limit` (integer, optional): Pagination limit

**Response** (200 OK):
```json
{
  "data": [
    {
      "id": 1,
      "name": "Jane Smith",
      "phone": "+1-555-123-4567",
      "email": "jane.smith@example.com",
      "project_id": 1,
      "call_count": 2,
      "last_call_at": "2024-03-12T09:00:00Z",
      "status": "interested",
      "created_at": "2024-03-12T10:30:00Z"
    }
  ],
  "total": 250,
  "skip": 0,
  "limit": 100
}
```

---

### GET /prospects/{prospect_id}

Get detailed prospect information.

**Headers**:
```
Authorization: Bearer <token>
```

**Path Parameters**:
- `prospect_id` (integer): Prospect ID

**Response** (200 OK):
```json
{
  "id": 1,
  "name": "Jane Smith",
  "phone": "+1-555-123-4567",
  "email": "jane.smith@example.com",
  "project_id": 1,
  "call_count": 2,
  "status": "interested",
  "metadata": {
    "property_type": "residential",
    "zip_code": "90210"
  },
  "call_history": [
    {
      "id": 1,
      "campaign_id": 1,
      "call_date": "2024-03-12T09:00:00Z",
      "duration": 245,
      "outcome": "interested"
    }
  ],
  "created_at": "2024-03-12T10:30:00Z"
}
```

---

### PUT /prospects/{prospect_id}

Update prospect information.

**Headers**:
```
Authorization: Bearer <token>
```

**Path Parameters**:
- `prospect_id` (integer): Prospect ID

**Request Body**:
```json
{
  "name": "Jane Smith-Johnson",
  "email": "jane.updated@example.com",
  "phone": "+1-555-999-9999",
  "metadata": {
    "property_type": "luxury_residential"
  }
}
```

**Response** (200 OK):
```json
{
  "id": 1,
  "name": "Jane Smith-Johnson",
  "email": "jane.updated@example.com",
  "phone": "+1-555-999-9999",
  "updated_at": "2024-03-12T11:00:00Z"
}
```

---

### DELETE /prospects/{prospect_id}

Delete a prospect.

**Headers**:
```
Authorization: Bearer <token>
```

**Path Parameters**:
- `prospect_id` (integer): Prospect ID

**Response** (200 OK):
```json
{
  "message": "Prospect deleted successfully"
}
```

---

## Calls Endpoints

### POST /calls/make-call

Initiate a single call to a prospect.

**Headers**:
```
Authorization: Bearer <token>
```

**Request Body**:
```json
{
  "prospect_id": 1,
  "campaign_id": 1
}
```

**Parameters**:
- `prospect_id` (integer, required): Prospect ID
- `campaign_id` (integer, required): Campaign ID

**Response** (200 OK):
```json
{
  "call_id": "call_abc123xyz789",
  "prospect_id": 1,
  "campaign_id": 1,
  "status": "initiated",
  "initiated_at": "2024-03-12T11:00:00Z",
  "message": "Call initiated successfully"
}
```

---

### POST /calls/start-campaign

Start batch calling for a campaign.

**Headers**:
```
Authorization: Bearer <token>
```

**Request Body**:
```json
{
  "campaign_id": 1,
  "batch_size": 20
}
```

**Parameters**:
- `campaign_id` (integer, required): Campaign ID
- `batch_size` (integer, optional): Number of calls to initiate (default: 10)

**Response** (200 OK):
```json
{
  "campaign_id": 1,
  "status": "executing",
  "initiated_calls": 20,
  "message": "Campaign execution started",
  "execution_id": "exec_xyz123"
}
```

---

### GET /calls/logs

Get call history logs.

**Headers**:
```
Authorization: Bearer <token>
```

**Query Parameters**:
- `campaign_id` (integer, optional): Filter by campaign
- `status` (string, optional): Filter by status (completed, failed, pending, initiated)
- `start_date` (string, optional): Filter by start date (ISO format)
- `end_date` (string, optional): Filter by end date (ISO format)
- `skip` (integer, optional): Pagination offset
- `limit` (integer, optional): Pagination limit

**Response** (200 OK):
```json
{
  "data": [
    {
      "id": 1,
      "call_id": "call_abc123xyz789",
      "prospect_id": 1,
      "prospect_name": "Jane Smith",
      "campaign_id": 1,
      "status": "completed",
      "outcome": "interested",
      "call_date": "2024-03-12T09:00:00Z",
      "duration": 245,
      "notes": "Prospect showed interest in property"
    }
  ],
  "total": 1500,
  "skip": 0,
  "limit": 100
}
```

---

### GET /calls/{conversation_id}/audio

Retrieve call audio recording.

**Headers**:
```
Authorization: Bearer <token>
```

**Path Parameters**:
- `conversation_id` (string): Conversation/Call ID

**Response** (200 OK):
```
[Audio file stream - MP3 format]
Content-Type: audio/mpeg
Content-Disposition: attachment; filename="call_abc123.mp3"
```

---

### GET /calls/{conversation_id}/chat

Retrieve conversation transcript.

**Headers**:
```
Authorization: Bearer <token>
```

**Path Parameters**:
- `conversation_id` (string): Conversation/Call ID

**Response** (200 OK):
```json
{
  "conversation_id": "call_abc123xyz789",
  "messages": [
    {
      "timestamp": "2024-03-12T09:00:00Z",
      "speaker": "agent",
      "message": "Hello, this is your friendly real estate agent..."
    },
    {
      "timestamp": "2024-03-12T09:00:15Z",
      "speaker": "prospect",
      "message": "Hi, how can I help you?"
    }
  ],
  "transcript": "Full transcript text...",
  "duration": 245
}
```

---

### PUT /calls/{call_id}/outcome

Update call outcome and disposition.

**Headers**:
```
Authorization: Bearer <token>
```

**Path Parameters**:
- `call_id` (string): Call ID

**Request Body**:
```json
{
  "outcome": "interested",
  "notes": "Prospect mentioned interest in viewing properties",
  "follow_up_date": "2024-03-15T14:00:00Z"
}
```

**Parameters**:
- `outcome` (string, required): Outcome type (interested, not_interested, callback_requested, no_answer, voicemail)
- `notes` (string, optional): Additional notes
- `follow_up_date` (string, optional): Scheduled follow-up date

**Response** (200 OK):
```json
{
  "call_id": "call_abc123xyz789",
  "outcome": "interested",
  "notes": "Prospect mentioned interest in viewing properties",
  "follow_up_date": "2024-03-15T14:00:00Z",
  "updated_at": "2024-03-12T11:00:00Z"
}
```

---

### POST /calls/refresh-outcomes

Refresh call outcomes from external system.

**Headers**:
```
Authorization: Bearer <token>
```

**Response** (200 OK):
```json
{
  "message": "Call outcomes refreshed successfully",
  "updated_count": 127,
  "refreshed_at": "2024-03-12T11:00:00Z"
}
```

---

### GET /calls/hot-prospects

Get list of interested prospects from recent calls.

**Headers**:
```
Authorization: Bearer <token>
```

**Query Parameters**:
- `project_id` (integer, optional): Filter by project
- `campaign_id` (integer, optional): Filter by campaign
- `days` (integer, optional): Last N days (default: 7)
- `skip` (integer, optional): Pagination offset
- `limit` (integer, optional): Pagination limit

**Response** (200 OK):
```json
{
  "data": [
    {
      "id": 1,
      "name": "Jane Smith",
      "phone": "+1-555-123-4567",
      "email": "jane.smith@example.com",
      "project_id": 1,
      "last_call_date": "2024-03-12T09:00:00Z",
      "outcome": "interested",
      "call_count": 2
    }
  ],
  "total": 85,
  "skip": 0,
  "limit": 100
}
```

---

### GET /calls/voices/list

List available ElevenLabs voice options.

**Headers**:
```
Authorization: Bearer <token>
```

**Response** (200 OK):
```json
{
  "voices": [
    {
      "voice_id": "EXAVITQu4vr4xnSDxMaL",
      "name": "Aria",
      "accent": "American",
      "age": "young adult",
      "gender": "female"
    },
    {
      "voice_id": "TxGEqA2bVvQvmKgjYZWJ",
      "name": "Roger",
      "accent": "American",
      "age": "middle-aged",
      "gender": "male"
    }
  ],
  "total": 15
}
```

---

## Documents Endpoints

### POST /documents/upload

Upload and process a document.

**Headers**:
```
Authorization: Bearer <token>
Content-Type: multipart/form-data
```

**Form Parameters**:
- `file` (file, required): PDF, DOCX, or image file
- `project_id` (integer, required): Project ID
- `document_type` (string, optional): Type of document (listing, agreement, etc.)

**Supported Formats**:
- PDF (.pdf)
- Word (.docx)
- Images (.jpg, .png)

**Response** (201 Created):
```json
{
  "id": 1,
  "filename": "property_listing.pdf",
  "document_type": "listing",
  "project_id": 1,
  "file_size": 2048576,
  "status": "processed",
  "extracted_text": "Property details...",
  "page_count": 5,
  "created_at": "2024-03-12T10:30:00Z"
}
```

---

### GET /documents

List documents for a project.

**Headers**:
```
Authorization: Bearer <token>
```

**Query Parameters**:
- `project_id` (integer, required): Project ID
- `document_type` (string, optional): Filter by document type
- `skip` (integer, optional): Pagination offset
- `limit` (integer, optional): Pagination limit

**Response** (200 OK):
```json
{
  "data": [
    {
      "id": 1,
      "filename": "property_listing.pdf",
      "document_type": "listing",
      "project_id": 1,
      "file_size": 2048576,
      "status": "processed",
      "page_count": 5,
      "created_at": "2024-03-12T10:30:00Z"
    }
  ],
  "total": 12,
  "skip": 0,
  "limit": 100
}
```

---

### GET /documents/{document_id}

Get document details.

**Headers**:
```
Authorization: Bearer <token>
```

**Path Parameters**:
- `document_id` (integer): Document ID

**Response** (200 OK):
```json
{
  "id": 1,
  "filename": "property_listing.pdf",
  "document_type": "listing",
  "project_id": 1,
  "file_size": 2048576,
  "status": "processed",
  "extracted_text": "Property details...",
  "page_count": 5,
  "metadata": {
    "address": "123 Main St, Los Angeles, CA 90210",
    "price": "$1,200,000"
  },
  "created_at": "2024-03-12T10:30:00Z"
}
```

---

### GET /documents/{document_id}/text

Retrieve extracted text from a document.

**Headers**:
```
Authorization: Bearer <token>
```

**Path Parameters**:
- `document_id` (integer): Document ID

**Response** (200 OK):
```
Plain text content of the document...
```

---

### POST /documents/{document_id}/reprocess

Reprocess a document to update text extraction.

**Headers**:
```
Authorization: Bearer <token>
```

**Path Parameters**:
- `document_id` (integer): Document ID

**Response** (200 OK):
```json
{
  "id": 1,
  "status": "processed",
  "extracted_text": "Updated extracted text...",
  "reprocessed_at": "2024-03-12T11:00:00Z",
  "message": "Document reprocessed successfully"
}
```

---

### DELETE /documents/{document_id}

Delete a document.

**Headers**:
```
Authorization: Bearer <token>
```

**Path Parameters**:
- `document_id` (integer): Document ID

**Response** (200 OK):
```json
{
  "message": "Document deleted successfully"
}
```

---

## Dashboard Endpoints

### GET /dashboard/stats

Get overall platform statistics and dashboard data.

**Headers**:
```
Authorization: Bearer <token>
```

**Query Parameters**:
- `period` (string, optional): Time period (today, week, month, all)

**Response** (200 OK):
```json
{
  "total_projects": 5,
  "total_campaigns": 12,
  "active_campaigns": 3,
  "total_prospects": 1500,
  "total_calls": 2345,
  "completed_calls": 1890,
  "successful_calls": 945,
  "interested_prospects": 287,
  "callback_requested": 156,
  "hot_prospects": 287,
  "pending_calls": 45,
  "overall_success_rate": 49.95,
  "avg_call_duration": 234,
  "total_call_minutes": 441480,
  "period": "all",
  "generated_at": "2024-03-12T11:00:00Z"
}
```

---

## Data Models

### User Model

```json
{
  "id": 1,
  "email": "user@example.com",
  "name": "User Name",
  "created_at": "2024-03-12T10:30:00Z",
  "updated_at": "2024-03-12T10:30:00Z"
}
```

### Project Model

```json
{
  "id": 1,
  "name": "Project Name",
  "description": "Project Description",
  "user_id": 1,
  "campaign_count": 3,
  "prospect_count": 100,
  "created_at": "2024-03-12T10:30:00Z",
  "updated_at": "2024-03-12T10:30:00Z"
}
```

### Campaign Model

```json
{
  "id": 1,
  "name": "Campaign Name",
  "project_id": 1,
  "description": "Campaign Description",
  "status": "active",
  "voice_id": "EXAVITQu4vr4xnSDxMaL",
  "agent_prompt": "Agent system prompt...",
  "total_prospects": 100,
  "completed_calls": 85,
  "successful_calls": 42,
  "failed_calls": 5,
  "interested_prospects": 15,
  "callback_requested": 10,
  "success_rate": 49.4,
  "created_at": "2024-03-12T10:30:00Z",
  "updated_at": "2024-03-12T10:30:00Z"
}
```

### Prospect Model

```json
{
  "id": 1,
  "name": "Prospect Name",
  "phone": "+1-555-123-4567",
  "email": "prospect@example.com",
  "project_id": 1,
  "call_count": 2,
  "status": "interested",
  "metadata": {
    "property_type": "residential",
    "zip_code": "90210"
  },
  "created_at": "2024-03-12T10:30:00Z",
  "updated_at": "2024-03-12T10:30:00Z"
}
```

### Call Model

```json
{
  "id": 1,
  "call_id": "call_abc123xyz789",
  "prospect_id": 1,
  "campaign_id": 1,
  "status": "completed",
  "outcome": "interested",
  "call_date": "2024-03-12T09:00:00Z",
  "duration": 245,
  "notes": "Call notes...",
  "follow_up_date": "2024-03-15T14:00:00Z",
  "created_at": "2024-03-12T10:30:00Z"
}
```

### Document Model

```json
{
  "id": 1,
  "filename": "document.pdf",
  "document_type": "listing",
  "project_id": 1,
  "file_size": 2048576,
  "status": "processed",
  "extracted_text": "Extracted content...",
  "page_count": 5,
  "metadata": {},
  "created_at": "2024-03-12T10:30:00Z",
  "updated_at": "2024-03-12T10:30:00Z"
}
```

---

## Rate Limiting

API rate limits are as follows:

- **Standard users**: 1000 requests per hour
- **Bulk operations**: 100 requests per hour
- **Authentication**: 20 requests per minute per IP

Rate limit headers are included in responses:
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1710300000
```

---

## Pagination

List endpoints support pagination with the following parameters:

- `skip` (integer): Number of items to skip (default: 0)
- `limit` (integer): Maximum items to return (default: 100, max: 1000)

**Example**:
```
GET /api/v1/projects?skip=0&limit=50
```

---

## Best Practices

1. **Token Management**: Store tokens securely and refresh before expiration
2. **Error Handling**: Always handle error responses appropriately
3. **Rate Limiting**: Implement exponential backoff for rate-limited responses
4. **Bulk Operations**: Use bulk endpoints for large data imports
5. **Caching**: Cache frequently accessed data on the client side
6. **Pagination**: Always use pagination for list endpoints
7. **Validation**: Validate data before sending to the API

---

## Support & Feedback

For issues, questions, or feedback, please contact support@realestateagent.com

**Version**: 1.0.0  
**Last Updated**: March 2024
