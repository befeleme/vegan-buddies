#!/usr/bin/env python3
"""
Environment setup script for Vegan Buddies application.
This script generates secure environment variables for database credentials and JWT secret key.
"""

import os
import secrets
import string
import subprocess
import sys
from pathlib import Path

def generate_secret_key(length=32):
    """Generate a secure random secret key for JWT tokens."""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def generate_db_password(length=16):
    """Generate a secure random password for the database."""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def create_env_file():
    """Create .env file with secure credentials."""
    env_file = Path('.env')
    
    if env_file.exists():
        print("⚠️  .env file already exists!")
        response = input("Do you want to overwrite it? (y/N): ").strip().lower()
        if response != 'y':
            print("❌ Setup cancelled.")
            return False
    
    # Generate secure credentials
    secret_key = generate_secret_key()
    db_password = generate_db_password()
    
    # Create .env file content
    env_content = f"""# Vegan Buddies Environment Configuration
# Generated automatically - DO NOT commit to version control

# JWT Secret Key (keep this secret!)
SECRET_KEY={secret_key}

# Database Configuration
DATABASE_URL=postgresql://postgres:{db_password}@postgres:5432/vegan_buddies
POSTGRES_DB=vegan_buddies
POSTGRES_USER=postgres
POSTGRES_PASSWORD={db_password}

# Frontend Configuration
REACT_APP_API_URL=http://localhost:8000
"""
    
    try:
        with open(env_file, 'w') as f:
            f.write(env_content)
        
        print("✅ Environment file created successfully!")
        print(f"📁 Created: {env_file.absolute()}")
        print()
        print("🔐 Generated credentials:")
        print(f"   Database Password: {db_password}")
        print(f"   JWT Secret Key: {secret_key[:8]}...")
        print()
        print("⚠️  IMPORTANT:")
        print("   - Keep these credentials secure!")
        print("   - The .env file is automatically ignored by git")
        print("   - Do not share these credentials")
        print()
        print("🚀 Next steps:")
        print("   1. Run: docker-compose up")
        print("   2. Run: python create_admin.py")
        print("   3. Open: http://localhost:3000")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")
        return False

def check_docker_compose():
    """Check if docker-compose is available."""
    try:
        subprocess.run(['docker-compose', '--version'], 
                      capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def main():
    print("🌱 Vegan Buddies Environment Setup")
    print("=" * 40)
    print()
    
    # Check if docker-compose is available
    if not check_docker_compose():
        print("❌ Docker Compose not found!")
        print("Please install Docker and Docker Compose first.")
        print("Visit: https://docs.docker.com/compose/install/")
        sys.exit(1)
    
    # Create .env file
    if create_env_file():
        print()
        print("🎉 Setup complete! You can now start the application.")
    else:
        print("❌ Setup failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
