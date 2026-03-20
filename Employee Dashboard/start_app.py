import subprocess
import sys
import os

def main():
    """Main function to run the Streamlit dashboard application."""
    try:
        # Get the directory of this script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # Path to the main dashboard app
        dashboard_path = os.path.join(script_dir, "dashboard_app.py")
        
        # Check if dashboard_app.py exists
        if not os.path.exists(dashboard_path):
            print("Error: dashboard_app.py not found!")
            print("Please make sure the dashboard application exists.")
            return 1
            
        # Run the Streamlit app
        print("Starting Srashtikasoftware Employee Dashboard...")
        print("Please wait while the dashboard loads in your browser...")
        subprocess.run([sys.executable, "-m", "streamlit", "run", dashboard_path])
        
    except KeyboardInterrupt:
        print("\nDashboard stopped by user.")
    except Exception as e:
        print(f"Error running dashboard: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())