#!/usr/bin/env python3
"""
Quick setup script for EtsyNova project
Run this after cloning to get started quickly
"""

import subprocess
import sys
import os

def run_command(command, cwd=None):
    """Run a shell command"""
    print(f"Running: {command}")
    result = subprocess.run(command, shell=True, cwd=cwd)
    if result.returncode != 0:
        print(f"Error running command: {command}")
        sys.exit(1)

def main():
    print("🚀 EtsyNova Quick Setup\n")
    
    # Check if Docker is installed
    try:
        subprocess.run(["docker", "--version"], check=True, capture_output=True)
        print("✅ Docker is installed")
    except:
        print("❌ Docker is not installed. Please install Docker Desktop first.")
        print("   Visit: https://www.docker.com/products/docker-desktop")
        sys.exit(1)
    
    # Create .env from example
    if not os.path.exists(".env"):
        if os.path.exists(".env.example"):
            print("📝 Creating .env file...")
            with open(".env.example", "r") as f:
                env_content = f.read()
            
            # Set mock mode by default
            env_content = env_content.replace("MOCK_MODE=false", "MOCK_MODE=true")
            
            with open(".env", "w") as f:
                f.write(env_content)
            print("✅ Created .env file with mock mode enabled")
        else:
            print("⚠️  No .env.example found")
    
    # Start Docker Compose
    print("\n🐳 Starting Docker containers...")
    print("This might take a few minutes on first run...\n")
    run_command("docker-compose up -d --build")
    
    print("\n✅ Setup complete!")
    print("\n📱 Access your applications:")
    print("   Frontend: http://localhost:3000")
    print("   API Docs: http://localhost:8000/docs")
    print("\n💡 Tips:")
    print("   - Default login: Use email from .env file")
    print("   - Mock mode is enabled for testing")
    print("   - Run 'docker-compose logs -f' to see logs")
    print("   - Run 'docker-compose down' to stop services")

if __name__ == "__main__":
    main()
