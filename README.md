# Real Estate Caller Agent

An intelligent automated calling agent for real estate prospecting and lead management. This platform combines a FastAPI backend with a React frontend to provide a comprehensive solution for running AI-powered calling campaigns.

## 🚀 Features

- **AI-Powered Calling**: Automated calling campaigns with intelligent conversation management
- **Campaign Management**: Create, activate, pause, and manage multiple calling campaigns
- **Contact Lists & Prospects**: Upload documents and manage prospect lists
- **Call Analytics**: Comprehensive dashboard with campaign statistics and call logs
- **Audio & Chat History**: Review conversations, audio recordings, and chat interactions
- **User Authentication**: Secure login and user management
- **Voice Selection**: Choose from multiple voice options for your agents
- **Real-time Webhooks**: Integration with external calling services via webhooks

## 📋 Tech Stack

### Backend
- **Framework**: FastAPI (Python)
- **Database**: SQL-based (via SQLAlchemy ORM)
- **Containerization**: Docker
- **Logging**: JSON-based structured logging

### Frontend
- **Framework**: React 18 with Vite
- **Styling**: Tailwind CSS
- **Build Tool**: Vite
- **State Management**: Zustand (authStore)
- **Containerization**: Docker & Nginx

## 🏗️ Project Structure

```
Real_estate_Caller_Agent/
├── Backend/                    # FastAPI application
│   ├── src/
│   │   └── app/
│   │       ├── auth/          # Authentication & user management
│   │       ├── calls/         # Call management endpoints
│   │       ├── campaigns/     # Campaign CRUD operations
│   │       ├── database/      # Database models & configuration
│   │       ├── documents/     # Document upload & management
│   │       ├── projects/      # Project management
│   │       ├── prospects/     # Prospect management
│   │       ├── dashboard/     # Analytics & statistics
│   │       ├── common/        # Shared utilities & settings
│   │       └── API.py         # Main API router
│   ├── main.py               # Application entry point
│   ├── pyproject.toml        # Dependencies & project config
│   ├── docker-compose.yml    # Docker composition
│   └── DockerFile            # Backend container image
├── Frontend/                  # React application
│   ├── src/
│   │   ├── components/       # Reusable React components
│   │   ├── pages/            # Page components
│   │   ├── services/         # API client services
│   │   ├── store/            # State management
│   │   └── App.jsx           # Root component
│   ├── package.json          # NPM dependencies
│   ├── vite.config.js        # Vite configuration
│   ├── tailwind.config.js    # Tailwind CSS configuration
│   ├── docker-compose.yml    # Frontend container setup
│   └── DockerFile            # Frontend container image
└── README.md                  # This file
```

## 📦 Prerequisites

- **Docker** & **Docker Compose** (for containerized setup)
- **Python 3.9+** (for local backend development)
- **Node.js 16+** (for local frontend development)
- **pip** and **npm/yarn** (package managers)

## 🛠️ Installation & Setup

### Option 1: Docker (Recommended)

The easiest way to get started is using Docker Compose:

```bash
# From the project root directory
docker-compose -f Backend/docker-compose.yml -f Frontend/docker-compose.yml up --build
```

This will:
- Build and start the FastAPI backend (typically on `http://localhost:8000`)
- Build and start the React frontend (typically on `http://localhost:3000` or port defined in nginx)
- Set up all required services

### Option 2: Local Development

#### Backend Setup

1. Navigate to the Backend directory:
   ```bash
   cd Backend
   ```

2. Create and activate a virtual environment:
   ```bash
   uv sync
   ```

3. Configure environment variables in `config.yml`

4. Run the server:
   ```bash
   python main.py
   ```

#### Frontend Setup

1. Navigate to the Frontend directory:
   ```bash
   cd Frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```

The frontend will be available at `http://localhost:5173` (Vite default)

## 📡 API Documentation

For detailed API documentation, see [Backend API Documentation](Backend/API_DOCUMENTATION.md)

### Key Endpoints

**Authentication**
- `POST /auth/register` - Register new user
- `POST /auth/login` - User login
- `PUT /auth/update` - Update user profile

**Campaigns**
- `GET /campaigns` - List all campaigns
- `POST /campaigns` - Create new campaign
- `GET /campaigns/{id}` - Get campaign details
- `PUT /campaigns/{id}` - Update campaign
- `DELETE /campaigns/{id}` - Delete campaign
- `POST /campaigns/{id}/activate` - Activate campaign
- `POST /campaigns/{id}/pause` - Pause campaign

**Calls**
- `GET /calls/logs` - Get call logs
- `POST /calls/single` - Make single call
- `GET /calls/audio/{conversation_id}` - Get call audio
- `GET /calls/chat/{conversation_id}` - Get chat history

**Prospects**
- `GET /prospects` - List prospects
- `GET /prospects/hot` - Get hot prospects

**Documents**
- `POST /documents/upload` - Upload document
- `GET /documents` - List documents
- `GET /documents/{id}` - Get document details

**Dashboard**
- `GET /dashboard/stats` - Get campaign statistics

## 🗄️ Database

The application uses SQLAlchemy ORM with database models defined in [Backend/src/app/database/models.py](Backend/src/app/database/models.py)

Configuration available in [Backend/config.yml](Backend/config.yml)

## 🔐 Authentication

The application uses JWT-based authentication with security utilities in the `auth/security.py` module. Refer to [Backend README](Backend/README.md) for detailed authentication flow.

## 📊 Logging

Structured JSON logging is configured via `logging.json`. Logs help track system operations and debug issues.

## 🚀 Deployment

### Docker Deployment

1. Build images:
   ```bash
   docker build -f Backend/DockerFile -t caller-agent-backend Backend/
   docker build -f Frontend/DockerFile -t caller-agent-frontend Frontend/
   ```

2. Run containers with proper environment configuration and port mapping

### Production Considerations

- Update `config.yml` with production settings
- Set environment variables for sensitive data
- Configure CORS properly for frontend/backend communication
- Use proper database backups and monitoring
- Set up SSL/TLS for HTTPS

## 📝 Configuration

Key configuration files:

- **Backend**: [config.yml](Backend/config.yml)
- **Logging**: [logging.json](Backend/logging.json)
- **Frontend**: [vite.config.js](Frontend/vite.config.js), [tailwind.config.js](Frontend/tailwind.config.js)

## 🛠️ Development

### Backend Development
- Hot reload available via FastAPI development server
- Use database migrations as needed
- Check logs in structured JSON format

### Frontend Development
- Hot reload available via Vite
- Component structure in `src/components/` and `src/pages/`
- API calls centralized in `src/services/api.js`

## 📚 Additional Documentation

- [Backend Documentation](Backend/README.md)
- [API Documentation](Backend/API_DOCUMENTATION.md)

## 🐛 Troubleshooting

**Port conflicts**: Update port mappings in docker-compose.yml or configure environment variables

**Database connection issues**: Verify database URL in config.yml and ensure database service is running

**Frontend can't connect to backend**: Check API endpoint configuration in [Frontend/src/services/api.js](Frontend/src/services/api.js)

## 📧 Support & Issues

For bugs or feature requests, please check existing issues or create a new one in the repository.

---
