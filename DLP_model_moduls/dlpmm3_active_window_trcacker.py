import time
import win32gui
import win32con
import win32process
import psutil
from dlpmm1_logging.py import log_event

def start_window_tracker(user="admin", protected_titles=None):
    if protected_titles is None:
        protected_titles = ["Confidential"]
    
    last_hwnd = None
    
    while True:
        try:
            hwnd = win32gui.GetForegroundWindow()
            if hwnd != last_hwnd:
                title = win32gui.GetWindowText(hwnd)
                
                # Проверка защищенных заголовков
                if any(t in title for t in protected_titles):
                    log_event("active_window", "Protected file opened", "High", user)
                
                # Получение информации о процессе
                try:
                    pid = win32process.GetWindowThreadProcessId(hwnd)[1]
                    process = psutil.Process(pid)
                    process_name = process.name()
                    
                    # Логирование браузера
                    if "chrome.exe" in process_name.lower() or "firefox.exe" in process_name.lower():
                        log_event("active_window", f"Browser opened: {process_name}", "Medium", user)
                    else:
                        log_event("active_window", f"App focused: {process_name}", "Low", user)
                except:
                    pass
                
                last_hwnd = hwnd
        except Exception as e:
            print(f"Window tracking error: {e}")
        
        time.sleep(0.5)

if __name__ == "__main__":
    start_window_tracker()