import subprocess
import sys
import time
import webbrowser
import threading
import argparse

def start_api_server():
    """Start the FastAPI backend server"""
    print("Starting API server...")
    api_process = subprocess.Popen(
        [sys.executable, "backend/api.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    # Wait briefly to let the API server start
    time.sleep(2)
    return api_process

def start_streamlit_ui():
    """Start the Streamlit UI"""
    print("Starting Streamlit UI...")
    streamlit_process = subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", "backend/streamlitUI.py", "--server.port", "8501"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    return streamlit_process

def open_browser():
    """Open web browser to Streamlit UI after a delay"""
    time.sleep(5)  # Give Streamlit time to start
    webbrowser.open("http://localhost:8501")

def show_help():
    """Display help information"""
    print("\nDelta Force Market Bot - Usage Options:")
    print("--------------------------------------")
    print("python run_app.py            : Run both API server and Streamlit UI")
    print("python run_app.py --api-only : Run only the API server (port 8000)")
    print("python run_app.py --ui-only  : Run only the Streamlit UI (port 8501)")
    print("python run_app.py --help     : Show this help message\n")

if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Delta Force Market Bot")
    parser.add_argument("--api-only", action="store_true", help="Run only the API server")
    parser.add_argument("--ui-only", action="store_true", help="Run only the Streamlit UI")
    args = parser.parse_args()

    # If help was requested, show help and exit
    if "--help" in sys.argv or "-h" in sys.argv:
        show_help()
        sys.exit(0)

    api_process = None
    streamlit_process = None

    # Determine what components to start based on arguments
    if args.api_only:
        # Start API server only
        api_process = start_api_server()
        print("API server running! Access API at http://localhost:8000")
        print("Press Ctrl+C to exit...")
        try:
            api_process.wait()
        except KeyboardInterrupt:
            print("\nShutting down API server...")
            api_process.terminate()
            print("API server stopped.")
    
    elif args.ui_only:
        # Start Streamlit UI only
        streamlit_process = start_streamlit_ui()
        # Open web browser after a delay
        browser_thread = threading.Thread(target=open_browser)
        browser_thread.daemon = True
        browser_thread.start()
        print("Streamlit UI running! Access UI at http://localhost:8501")
        print("Press Ctrl+C to exit...")
        try:
            streamlit_process.wait()
        except KeyboardInterrupt:
            print("\nShutting down Streamlit UI...")
            streamlit_process.terminate()
            print("Streamlit UI stopped.")
    
    else:
        # Start both API server and Streamlit UI (default behavior)
        api_process = start_api_server()
        streamlit_process = start_streamlit_ui()
        
        # Open web browser after a delay
        browser_thread = threading.Thread(target=open_browser)
        browser_thread.daemon = True
        browser_thread.start()
        
        try:
            # Wait for the processes to complete (which they won't unless killed)
            print("Application running! Access the UI at http://localhost:8501")
            print("API server running at http://localhost:8000")
            print("Press Ctrl+C to exit...")
            streamlit_process.wait()
        except KeyboardInterrupt:
            # Handle Ctrl+C gracefully
            print("\nShutting down services...")
            if api_process:
                api_process.terminate()
            if streamlit_process:
                streamlit_process.terminate()
            print("Application stopped.")
