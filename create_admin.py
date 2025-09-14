#!/usr/bin/env python3
"""
Script to create the initial admin user in the Vegan Buddies application.
Run this after starting the docker-compose services.
"""

import subprocess
import sys
import os
import secrets
import string
from passlib.context import CryptContext

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def generate_random_password(length=12):
    """Generate a secure random password."""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    password = ''.join(secrets.choice(alphabet) for _ in range(length))
    return password

def fix_existing_users():
    """Fix existing users that have NULL password_change_required values."""
    print("Checking for existing users with missing password_change_required field...")
    
    # SQL command to update existing users
    sql_command = "UPDATE users SET password_change_required = FALSE WHERE password_change_required IS NULL;"
    
    # Docker command to execute the SQL
    docker_command = [
        "docker-compose", "exec", "-T", "postgres", 
        "psql", "-U", "postgres", "-d", "vegan_buddies", 
        "-c", sql_command
    ]
    
    try:
        result = subprocess.run(docker_command, capture_output=True, text=True, check=True)
        if result.returncode == 0:
            print("✅ Fixed existing users")
        else:
            print("⚠️  Warning: Could not fix existing users (this is usually fine)")
    except Exception as e:
        print(f"⚠️  Warning: Could not fix existing users: {e}")

def create_admin_user(username="admin", email="admin@veganbuddies.com", password=None):
    """Create an admin user directly in the database via SQL."""
    
    # First, fix any existing users with NULL password_change_required
    fix_existing_users()
    
    # Generate random password if none provided
    if password is None:
        password = generate_random_password()
    
    # Hash the password
    hashed_password = pwd_context.hash(password)
    
    print(f"Creating admin user:")
    print(f"  Username: {username}")
    print(f"  Email: {email}")
    print(f"  Password: {password}")
    print()
    
    # SQL command to insert the user
    sql_command = f"INSERT INTO users (username, email, hashed_password, is_admin, password_change_required, created_at) VALUES ('{username}', '{email}', '{hashed_password}', true, false, NOW());"
    
    # Docker command to execute the SQL
    docker_command = [
        "docker-compose", "exec", "-T", "postgres", 
        "psql", "-U", "postgres", "-d", "vegan_buddies", 
        "-c", sql_command
    ]
    
    try:
        print("Executing SQL command...")
        result = subprocess.run(docker_command, capture_output=True, text=True, check=True)
        
        if result.returncode == 0:
            print("✅ Admin user created successfully!")
            print()
            print("🔐 IMPORTANT: Save these login credentials!")
            print("=" * 50)
            print(f"Username: {username}")
            print(f"Password: {password}")
            print("=" * 50)
            print()
            print("You can now login to the application:")
            print(f"  URL: http://localhost:3000")
            print(f"  Username: {username}")
            print(f"  Password: {password}")
        else:
            print("❌ Failed to create admin user:")
            print(result.stderr)
            
    except subprocess.CalledProcessError as e:
        print("❌ Error executing command:")
        print(f"Return code: {e.returncode}")
        print(f"Error output: {e.stderr}")
        print()
        print("Make sure docker-compose is running and the postgres service is up.")
        print("You can start it with: docker-compose up")
        
    except FileNotFoundError:
        print("❌ Docker Compose not found. Make sure Docker and Docker Compose are installed.")
        print()
        print("Manual method:")
        print("Run this command manually:")
        print(f'docker-compose exec postgres psql -U postgres -d vegan_buddies -c "{sql_command}"')

if __name__ == "__main__":
    if len(sys.argv) > 1:
        username = sys.argv[1]
    else:
        username = "admin"
    
    if len(sys.argv) > 2:
        email = sys.argv[2]
    else:
        email = "admin@veganbuddies.com"
    
    if len(sys.argv) > 3:
        password = sys.argv[3]
    else:
        password = None  # Will generate random password
    
    create_admin_user(username, email, password)
