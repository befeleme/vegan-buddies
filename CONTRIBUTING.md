# Contributing to Vegan Buddies

This document explains how to set up and run the Vegan Buddies application locally for development and contribution.

## Architecture

The application consists of:
- **Frontend**: React application running on port 3000
- **Backend**: FastAPI application running on port 8000
- **Database**: PostgreSQL running on port 5432

## Prerequisites

- Docker and Docker Compose installed on your system
- Python 3.7+ installed
- Git (for cloning the repository)

## Quick Start

1. **Clone the repository** (if you haven't already):
   ```bash
   git clone <repository-url>
   cd vegan-buddies
   ```

2. **Generate Environment Variables**:
   ```bash
   python setup_env.py
   ```
   This will create a `.env` file with secure database credentials and JWT secret keys.

3. **Start all services**:
   ```bash
   docker-compose up --build
   ```

   This command will:
   - Build the React frontend and FastAPI backend
   - Start PostgreSQL database with secure credentials
   - Start all services with hot reloading enabled

4. **Create Admin User**:
   ```bash
   python create_admin.py
   ```
   This will create an admin user with auto-generated credentials.

5. **Access the application**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## Environment Configuration

The application requires secure environment variables for database credentials and JWT secret keys. The `setup_env.py` script generates these automatically.

### What the setup_env.py script does:

- Generates secure database password
- Creates JWT secret key
- Sets up database connection URL
- Creates `.env` file (automatically ignored by git)
- Provides clear next steps

### Manual Environment Setup (Alternative)

If you prefer to set environment variables manually:

```bash
export SECRET_KEY="your-secure-secret-key-here"
export DATABASE_URL="postgresql://postgres:your-secure-password@postgres:5432/vegan_buddies"
export POSTGRES_PASSWORD="your-secure-password"
export REACT_APP_API_URL="http://localhost:8000"
```

**Important**: The `.env` file contains sensitive information and is automatically ignored by git.

## Development Workflow

### Making Changes

- **Frontend changes**: Edit files in the `frontend/` directory. Changes will be hot-reloaded automatically.
- **Backend changes**: Edit files in the `backend/` directory. Changes will be hot-reloaded automatically.
- **Database changes**: The database persists data in a Docker volume. To reset the database, run:
  ```bash
  docker-compose down -v
  docker-compose up --build
  ```

### Stopping the Application

```bash
docker-compose down
```

### Viewing Logs

```bash
# All services
docker-compose logs

# Specific service
docker-compose logs frontend
docker-compose logs backend
docker-compose logs postgres
```

## Project Structure

```
vegan-buddies/
├── frontend/                 # React application
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── services/        # API service functions
│   │   └── ...
│   ├── Dockerfile
│   └── package.json
├── backend/                 # FastAPI application
│   ├── main.py             # FastAPI app entry point
│   ├── models.py           # SQLAlchemy models
│   ├── schemas.py          # Pydantic schemas
│   ├── database.py         # Database configuration
│   ├── requirements.txt
│   └── Dockerfile
├── docker-compose.yml      # Docker Compose configuration
└── CONTRIBUTING.md         # This file
```

## API Endpoints

- `POST /auth/login` - User login
- `GET /users` - Get all users (requires authentication)
- `POST /users` - Create new admin user (requires authentication)
- `GET /me` - Get current user info (requires authentication)

## Troubleshooting

### Environment Not Configured Error

If you see "Environment Not Configured" error in the frontend:
1. Run `python setup_env.py`
2. Restart the application with `docker-compose up`

### No Admin Users Error

If you see "No Admin Users Found" error:
1. Make sure the database is running (`docker-compose up`)
2. Run `python create_admin.py`
3. Refresh the page

### Port Already in Use
If you get port conflicts, you can modify the ports in `docker-compose.yml`:
```yaml
ports:
  - "3001:3000"  # Change frontend port
  - "8001:8000"  # Change backend port
  - "5433:5432"  # Change database port
```

### Database Connection Issues
- Ensure PostgreSQL container is running: `docker-compose ps`
- Check database logs: `docker-compose logs postgres`
- Verify database URL in backend environment variables
- Check the health endpoint: http://localhost:8000/health

### Frontend Not Loading
- Check if backend is running: `curl http://localhost:8000`
- Verify CORS settings in `backend/main.py`
- Check browser console for errors
- Ensure environment variables are properly set

### Health Check Endpoint

The application provides a health check endpoint at http://localhost:8000/health that shows:
- Environment configuration status
- Admin user count
- Overall system health

## Security Notes

- All passwords are auto-generated and secure
- Environment variables are properly isolated in `.env` file
- Credentials are never committed to git
- Users are required to change password on first login
- JWT tokens expire after 30 minutes
- All user creation endpoints require authentication

## Next Steps

Once you have the application running:
1. Login with the admin user
2. Create additional admin users through the web interface
3. Explore the API documentation at http://localhost:8000/docs
4. Start developing your features!
