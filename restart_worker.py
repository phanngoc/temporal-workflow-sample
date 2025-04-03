"""
Script để khởi động lại worker với code mới
"""
import os
import signal
import subprocess
import time

def restart_worker():
    # Tìm process worker hiện tại
    try:
        # Tìm PID của worker
        worker_pid = subprocess.check_output(
            "ps aux | grep 'python -m app.workers.worker' | grep -v grep | awk '{print $2}'", 
            shell=True
        ).decode().strip()
        
        if worker_pid:
            print(f"Đang dừng worker với PID {worker_pid}...")
            # Gửi signal SIGTERM để dừng worker
            os.kill(int(worker_pid), signal.SIGTERM)
            print("Đợi worker dừng hoàn toàn...")
            time.sleep(2)
    except Exception as e:
        print(f"Không tìm thấy worker đang chạy: {str(e)}")
    
    # Khởi động worker mới
    print("Đang khởi động worker mới...")
    subprocess.Popen(["python", "-m", "app.workers.worker"])
    print("Worker đã được khởi động lại!")

if __name__ == "__main__":
    restart_worker() 