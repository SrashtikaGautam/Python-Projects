#!/usr/bin/env python3
"""
Runner script for the Glamour Salon application.
This script sets up the environment and runs the main Streamlit app.
"""

import subprocess
import sys
import os

def main():
    print("🚀 Starting Glamour Salon Application...")
    print("=" * 50)
    
    # Check if required packages are installed
    try:
        import streamlit
        import pandas
        import sqlite3
        import plotly
        from PIL import Image
        print("✅ All required packages are available")
    except ImportError as e:
        print("❌ Missing required packages. Please install them using:")
        print("   pip install -r requirements.txt")
        return 1
    
    # Initialize the database
    try:
        print("🔧 Initializing database...")
        from app_restored import init_db
        init_db()
        print("✅ Database initialized successfully")
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        return 1
    
    # Run the Streamlit app
    try:
        print("🎨 Launching Glamour Salon App...")
        print("=" * 50)
        print("The app will open in your browser shortly.")
        print("Press Ctrl+C to stop the application.")
        print("=" * 50)
        
        # Run the Streamlit app
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "app_restored.py"
        ], check=True)
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running the application: {e}")
        return 1
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user.")
        return 0
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())