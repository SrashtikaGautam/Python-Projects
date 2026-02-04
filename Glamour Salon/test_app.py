#!/usr/bin/env python3
"""
Test script for the Glamour Salon application.
This script tests the database functionality and displays basic information.
"""

import sqlite3
import json

def test_database():
    """Test database connectivity and show basic information."""
    print("🧪 Testing Glamour Salon Database...")
    print("=" * 40)
    
    try:
        # Connect to database
        conn = sqlite3.connect('salon.db')
        cursor = conn.cursor()
        
        # Test 1: Show all tables
        print("📋 Database Tables:")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        for table in tables:
            print(f"  - {table[0]}")
            
            # Show table structure
            cursor.execute(f"PRAGMA table_info({table[0]});")
            columns = cursor.fetchall()
            for col in columns:
                print(f"    └─ {col[1]} ({col[2]})")
        print()
        
        # Test 2: Count records in each table
        print("📊 Record Counts:")
        for table in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table[0]};")
                count = cursor.fetchone()[0]
                print(f"  - {table[0]}: {count} records")
            except Exception as e:
                print(f"  - {table[0]}: Error counting records - {e}")
        print()
        
        # Test 3: Show sample services
        print("💇 Sample Services:")
        try:
            cursor.execute("SELECT name, price, duration FROM services LIMIT 5;")
            services = cursor.fetchall()
            for service in services:
                print(f"  - {service[0]}: ${service[1]} ({service[2]} mins)")
        except Exception as e:
            print(f"  Error fetching services: {e}")
        print()
        
        conn.close()
        print("✅ Database test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def show_config():
    """Display salon configuration."""
    print("🏢 Salon Configuration:")
    print("=" * 40)
    
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
        
        print(f"Name: {config['salon_name']}")
        print(f"Tagline: {config['tagline']}")
        print(f"Phone: {config['contact']['phone']}")
        print(f"Address: {config['contact']['address']}")
        print()
        print("⏰ Business Hours:")
        for day, hours in config['hours'].items():
            print(f"  - {day.replace('_', ' ').title()}: {hours}")
        
        print("✅ Configuration loaded successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error loading configuration: {e}")
        return False

def main():
    """Main test function."""
    print("🔍 Glamour Salon System Test")
    print("=" * 50)
    
    # Test configuration
    show_config()
    print()
    
    # Test database
    test_database()
    print()
    
    print("🏁 Test completed!")
    print("\n💡 To run the full application, execute:")
    print("   python run_app.py")

if __name__ == "__main__":
    main()