#!/usr/bin/env python3
"""
Database migration script to add the password_change_required column.
Run this after updating the models.
"""

import subprocess
import sys
import os

def run_migration():
    """Add the password_change_required column to the users table."""
    
    print("Adding password_change_required column to users table...")
    
    # SQL command to add the column
    sql_command = """
    ALTER TABLE users 
    ADD COLUMN IF NOT EXISTS password_change_required BOOLEAN DEFAULT TRUE;
    """
    
    # Docker command to execute the SQL
    docker_command = [
        "docker-compose", "exec", "-T", "postgres", 
        "psql", "-U", "postgres", "-d", "vegan_buddies", 
        "-c", sql_command
    ]
    
    try:
        print("Executing migration...")
        result = subprocess.run(docker_command, capture_output=True, text=True, check=True)
        
        if result.returncode == 0:
            print("✅ Migration completed successfully!")
            print("The password_change_required column has been added to the users table.")
        else:
            print("❌ Migration failed:")
            print(result.stderr)
            
    except subprocess.CalledProcessError as e:
        print("❌ Error executing migration:")
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
    run_migration()
