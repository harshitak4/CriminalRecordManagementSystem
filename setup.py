import subprocess
import sys
import os

def install_dependencies():
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("Dependencies installed successfully.")
    except subprocess.CalledProcessError:
        print("Failed to install dependencies.")
        sys.exit(1)

def setup_directories():
    directories = ["keys", "data", "logs"]
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Created directory: {directory}")

def main():
    if not os.path.exists("requirements.txt"):
        print("requirements.txt not found. Please ensure it exists.")
        sys.exit(1)
    
    print("Starting setup...")
    install_dependencies()
    setup_directories()
    print("Setup complete. You can now run the nodes using main.py")

if __name__ == "__main__":
    main()
