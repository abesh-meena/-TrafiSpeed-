#!/usr/bin/env python3
"""
Traffic Speed Detection Web Application
Run this script to start the web server
"""

import os
import sys

def check_dependencies():
    """Check if required packages are installed"""
    required_packages = ['flask', 'cv2']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("Missing required packages:")
        for package in missing_packages:
            print(f"  - {package}")
        print("\nPlease install them using:")
        print("pip install -r requirements.txt")
        return False
    
    print("Note: dlib is optional for advanced tracking. Basic functionality will work without it.")
    return True

def check_files():
    """Check if required files exist"""
    required_files = ['app.py', 'templates/index.html']
    missing_files = []
    
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    # Check for vech.xml but don't fail if missing
    if not os.path.exists('vech.xml'):
        print("Warning: vech.xml not found. Advanced detection will be disabled.")
    
    if missing_files:
        print("Missing required files:")
        for file in missing_files:
            print(f"  - {file}")
        return False
    
    return True

def main():
    print("=== Traffic Speed Detection Web Application ===")
    print()
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check files
    if not check_files():
        sys.exit(1)
    
    # Create necessary directories
    os.makedirs('uploads', exist_ok=True)
    os.makedirs('outputs', exist_ok=True)
    
    print("All checks passed!")
    print("Starting web server...")
    print("Access the application at: http://localhost:5000")
    print("Press Ctrl+C to stop the server")
    print()
    
    # Import and run the Flask app
    from app import app
    app.run(debug=True, host='0.0.0.0', port=5000)

if __name__ == '__main__':
    main()
