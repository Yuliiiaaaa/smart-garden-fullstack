import subprocess
import sys
import time
import webbrowser
from pathlib import Path
import os

def find_npm():
    """Находит npm в системе"""
    # Пробуем разные пути
    possible_paths = [
        "npm",  # Если в PATH
        "npm.cmd",  # Windows
        os.path.join(os.environ.get("APPDATA", ""), "npm", "npm.cmd"),
        os.path.join(os.environ.get("ProgramFiles", ""), "nodejs", "npm.cmd"),
        os.path.join(os.environ.get("ProgramFiles(x86)", ""), "nodejs", "npm.cmd"),
    ]
    
    for npm_path in possible_paths:
        try:
            subprocess.run([npm_path, "--version"], capture_output=True, check=True)
            return npm_path
        except:
            continue
    
    return None

def main():
    print("Starting Smart Garden Platform...")
    
    # Ищем npm
    npm_path = find_npm()
    if not npm_path:
        print("ERROR: npm not found. Install Node.js or add to PATH")
        print("Download Node.js from: https://nodejs.org/")
        return
    
    print(f"Found npm: {npm_path}")
    
    # Проверяем frontend
    frontend_dir = Path("frontend")
    if not frontend_dir.exists():
        print("ERROR: frontend/ directory not found")
        return
    
    # Запускаем backend
    print("\n1. Starting backend server...")
    backend_process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"],
        cwd="backend/app",
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        shell=True  # Для Windows
    )
    
    time.sleep(8)
    
    if backend_process.poll() is not None:
        print("ERROR: Backend failed to start")
        output = backend_process.stdout.read()
        if output:
            print("Backend error:")
            print(output[:1500])
        return
    
    print("Backend running: http://localhost:8000")
    
    # Запускаем frontend
    print("\n2. Starting frontend server...")
    try:
        frontend_process = subprocess.Popen(
            [npm_path, "run", "dev"],
            cwd="frontend",
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            shell=True  # Для Windows
        )
        
        time.sleep(10)
        
        if frontend_process.poll() is not None:
            print("ERROR: Frontend failed to start")
            output = frontend_process.stdout.read()
            if output:
                print("Frontend error:")
                print(output[:1000])
            return
        
        print("Frontend running: http://localhost:3000")
        
    except Exception as e:
        print(f"ERROR starting frontend: {e}")
        print("Try running manually: cd frontend && npm run dev")
        return
    
    print("\n" + "="*50)
    print("SERVICES RUNNING:")
    print("- Frontend: http://localhost:3000")
    print("- Backend:  http://localhost:8000")
    print("- API Docs: http://localhost:8000/docs")
    print("="*50)
    print("\nPress Ctrl+C to stop")
    
    webbrowser.open("http://localhost:3000")
    
    try:
        while True:
            if backend_process.poll() is None:
                backend_line = backend_process.stdout.readline()
                if backend_line:
                    print(f"[BACKEND] {backend_line.strip()}")
            
            if frontend_process.poll() is None:
                frontend_line = frontend_process.stdout.readline()
                if frontend_line:
                    print(f"[FRONTEND] {frontend_line.strip()}")
            
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\nStopping services...")
        backend_process.terminate()
        frontend_process.terminate()
        print("Services stopped")

if __name__ == "__main__":
    main()