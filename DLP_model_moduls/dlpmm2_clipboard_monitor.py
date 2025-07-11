import time
import win32clipboard
import win32con
from dlpmm1_logging.py import log_event, get_current_time

def get_clipboard_files():
    files = []
    try:
        win32clipboard.OpenClipboard()
        if win32clipboard.IsClipboardFormatAvailable(win32con.CF_HDROP):
            files = win32clipboard.GetClipboardData(win32con.CF_HDROP)
    finally:
        win32clipboard.CloseClipboard()
    return files

def start_clipboard_monitor(user="admin", protected_paths=None):
    if protected_paths is None:
        protected_paths = ["C:\\Protected"]
    
    last_content = None
    
    while True:
        try:
            # Проверка текста
            try:
                win32clipboard.OpenClipboard()
                text_content = win32clipboard.GetClipboardData(win32con.CF_UNICODETEXT)
            except:
                text_content = None
            finally:
                win32clipboard.CloseClipboard()
            
            # Проверка файлов
            file_content = get_clipboard_files()
            
            # Обнаружение конфиденциальных данных
            if text_content and text_content != last_content:
                last_content = text_content
                # Здесь должна быть проверка на конфиденциальность
                # if contains_sensitive_data(text_content):
                log_event("clipboard", "Text copied", "Medium", user)
            
            if file_content:
                for file in file_content:
                    if any(p in file for p in protected_paths):
                        log_event("clipboard", f"Protected file copied: {file}", "High", user)
        except Exception as e:
            print(f"Clipboard error: {e}")
        
        time.sleep(1)

if __name__ == "__main__":
    start_clipboard_monitor()