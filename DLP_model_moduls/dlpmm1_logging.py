import os
import csv
import datetime

def get_current_time():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def ensure_file_exists(file_path):
    if not os.path.exists(file_path):
        with open(file_path, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['Timestamp', 'User', 'Module', 'Event', 'Mark'])

def log_event(module, event, mark, user, log_dir="logs"):
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, f"log_{module}.csv")
    
    ensure_file_exists(log_file)
    
    with open(log_file, 'a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow([get_current_time(), user, module, event, mark])