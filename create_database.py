#!/usr/bin/env python3
"""
Script to create the PostgreSQL database for InternSync API
Run this after installing PostgreSQL
"""

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def create_database():
    try:
        # Connect to PostgreSQL server (not to a specific database)
        connection = psycopg2.connect(
            host="localhost",
            port="5432",
            user="postgres",
            password="eoiHrfnvmomkrj34738"
        )
        
        # Enable autocommit to create database
        connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = connection.cursor()
        
        # Check if database exists
        cursor.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = 'internsync'")
        exists = cursor.fetchone()
        
        if exists:
            print("✅ Database 'internsync' already exists!")
        else:
            # Create the database
            cursor.execute("CREATE DATABASE internsync")
            print("✅ Database 'internsync' created successfully!")
        
        cursor.close()
        connection.close()
        
    except psycopg2.OperationalError as e:
        print(f"❌ Error: Could not connect to PostgreSQL server")
        print(f"Make sure PostgreSQL is installed and running")
        print(f"Error details: {e}")
    except Exception as e:
        print(f"❌ Error creating database: {e}")

if __name__ == "__main__":
    print("🔧 Creating PostgreSQL database for InternSync...")
    create_database()
