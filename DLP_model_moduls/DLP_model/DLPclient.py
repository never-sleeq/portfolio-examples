import socket
import os
import threading
import time
import queue
import win32clipboard
import csv
import datetime
import win32con
import win32gui
import psutil
from pynput import keyboard
import win32process
import json
import win32api
import win32file
import docx


#импорт прочих локальных модулей если надо


SERVER_IP = "192.168.30.11" #возможно сделать подгрузку ip сервера с json файла

SERVER_PORT = 6001
IDENTIFIER = os.getlogin()

LOG_CB = "C:\\Users\\{}\\DLP\\log_cb.csv".format(IDENTIFIER)
LOG_AW = "C:\\Users\\{}\\DLP\\log_aw.csv".format(IDENTIFIER)
LOG_KL = "C:\\Users\\{}\\DLP\\log_kl.csv".format(IDENTIFIER)
LOG_USB = "C:\\Users\\{}\\DLP\\log_usb.csv".format(IDENTIFIER)

#CONFIG_FILE = "C:\\Users\\{}\\DLP\\conf.json".format(IDENTIFIER)

FILE_ACTION_ADDED = 0x00000001
#FILE_ACTION_REMOVED = 0x00000002
FILE_ACTION_MODIFIED = 0x00000003
#FILE_ACTION_RENAMED_OLD_NAME = 0x00000004
#FILE_ACTION_RENAMED_NEW_NAME = 0x00000005

vault = ''
csv_files = []
bf = 0
sf = 0
kbinput = []
keyloggerp = None



# def exstnc(filePath):
# 	if not os.path.exists(filePath):
# 		with open(filePath, mode = 'w', newline='', encoding='utf-8') as file:
# 			writer = csv.writer(file)
# 			writer.writerow(['Timestamp', 'User', 'Module', 'Event', 'Mark'])

def exstnc(filePath):
	if not os.path.exists(filePath):
		with open(filePath, mode = 'w', newline='', encoding='utf-8') as file:
			writer = csv.writer(file)
			writer.writerow('')




def get_current_time():
	return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def csvcheck():
	global vault

	for filename in os.listdir(vault):
		if filename.endswith('.csv'):
			file_path = os.path.join(vault, filename)
			csv_files.append(file_path)

def csvCheckExpression(content):
	for fileP in csv_files:
		with open(fileP, mode = 'r', encoding='utf-8') as file:
			reader = csv.reader(file)
			for row in reader:
				if any(content in cell for cell in row):
					return True
	return False

def csvCheckExpressionInverse(content):
	for fileP in csv_files:
		with open(fileP, mode = 'r', encoding='utf-8') as file:
			reader = csv.reader(file)
			for row in reader:
				if any(cell in content for cell in row):
					return True
	return False

def logging(module, event, mark):

	if module == 'clipboard':
		file_exists = os.path.isfile(LOG_CB)
		with open(LOG_CB, mode='a', newline='', encoding='utf-8') as file:
			writer = csv.writer(file)
			writer.writerow([get_current_time(), IDENTIFIER, module, event, mark])

	elif module == 'active window':
		file_exists = os.path.isfile(LOG_AW)
		with open(LOG_AW, mode='a', newline='', encoding='utf-8') as file:
			writer = csv.writer(file)
			writer.writerow([get_current_time(), IDENTIFIER, module, event, mark])

	elif module == 'keylogger':
		file_exists = os.path.isfile(LOG_KL)
		with open(LOG_KL, mode='a', newline='', encoding='utf-8') as file:
			writer = csv.writer(file)
			writer.writerow([get_current_time(), IDENTIFIER, module, event, mark])

	elif module == 'usb':
		file_exists = os.path.isfile(LOG_USB)
		with open(LOG_USB, mode='a', newline='', encoding='utf-8') as file:
			writer = csv.writer(file)
			writer.writerow([get_current_time(), IDENTIFIER, module, event, mark])


def get_clipboard_files():
	files = []
	try:
		win32clipboard.OpenClipboard()
		if win32clipboard.IsClipboardFormatAvailable(win32con.CF_HDROP):
			files = win32clipboard.GetClipboardData(win32con.CF_HDROP)
	except Exception as e:
		print(f"Ошибка при проверке буфера обмена: {e}")
	finally:
		win32clipboard.CloseClipboard()

	return files

def process_file(file_path):
	if file_path.split('\\')[-1] in [f.split('\\')[-1] for f in csv_files]:
		logging('usb', f'Обнаружен защищенный файл: {file_path}', 'Средний уровень угрозы')

	if file_path.endswith(('.csv', '.txt')):
		with open(file_path, 'r', encoding='utf-8') as content_file:
			file_content = content_file.read()

		if not file_content.strip():
			print(f"Файл {file_path} пуст, пропускаем.")
			return

		if csvCheckExpressionInverse(file_content):
			logging('usb', f'Обнаружено содержимое конфиденциальной информации: {file_path}', 'Высокий уровень угрозы')
			os.remove(file_path)
			logging('usb', f'Файл удалён: {file_path}', 'Высокий уровень угрозы')

	elif file_path.endswith('.docx'):
		try:
			doc = docx.Document(file_path)
			file_content = '\n'.join([paragraph.text for paragraph in doc.paragraphs])

			if not file_content.strip():
				print(f"Файл {file_path} пуст, пропускаем.")
				return

			if csvCheckExpressionInverse(file_content):
				logging('usb', f'Обнаружено содержимое конфиденциальной информации: {file_path}', 'Высокий уровень угрозы')
				os.remove(file_path)
				logging('usb', f'Файл удалён: {file_path}', 'Высокий уровень угрозы')
		except Exception as e:
			print(f"Ошибка при обработке docx файла {file_path}: {e}")



def monitor_usb_drive(device):
	global csv_files
	print(device)

	hDir = win32file.CreateFile(
		device,
		win32con.GENERIC_READ,
		win32con.FILE_SHARE_READ | win32con.FILE_SHARE_WRITE | win32con.FILE_SHARE_DELETE,
		None,
		win32con.OPEN_EXISTING,
		win32con.FILE_FLAG_BACKUP_SEMANTICS,
		None
	)

	while True:
		try:
			
			if not os.path.exists(device):
				return

			results = win32file.ReadDirectoryChangesW(
				hDir,
				1024,
				True,
				win32con.FILE_NOTIFY_CHANGE_FILE_NAME |
				win32con.FILE_NOTIFY_CHANGE_LAST_WRITE,
				None,
				None
				)

			for action, file in results:
				full_path = os.path.join(device, file)

				if action in {FILE_ACTION_ADDED, FILE_ACTION_MODIFIED}:
					print(action)
					if os.path.isfile(full_path):
						process_file(full_path)
			results = []
			time.sleep(2)

		except Exception as e:
			print("юэсби модул:",e)
			time.sleep(1)

	win32file.CloseHandle(hDir)



def on_press(key):
	global kbinput
	global bf
	global keyloggerp
	try:
		if hasattr(key,'char') and key.char:
			kbinput.append(key.char)
		elif key == keyboard.Key.space:
			kbinput.append(' ')
		elif key == keyboard.Key.enter:
			original_text = ''.join(kbinput)
			if csvCheckExpression(original_text):
				os.system("taskkill /im chrome.exe /f")
				logging('keylogger', 'Ввёл в браузер корпоративную информацию', 'Высокий уровень угрозы')
			kbinput = []
		print(bf)
		if bf == 0:
			kbinput = []
			keyloggerp = None
			return False
	finally:
		pass




def KLModuleMainF():
	print("kl active.\n")
	with keyboard.Listener(on_press=on_press) as listener:
		print("salam aletkum")
		listener.join()


def USBModuleMainF():
	global vault
	last_devices = set()

	while True:
		try:
			drives = win32api.GetLogicalDriveStrings().split('\x00')
			usb_drives = [drive for drive in drives if win32file.GetDriveType(drive) == win32file.DRIVE_REMOVABLE]
			current_devices = set(usb_drives)

			new_devices = current_devices - last_devices
			for device in new_devices:
				logging('usb', f'Подключено устройство: {device}', 'Низкий уровень угрозы')
				usbDriveMonitoring = threading.Thread(target=monitor_usb_drive, args=(device,))
				usbDriveMonitoring.start()

			last_devices = current_devices

		except Exception as e:
			print("USB module: ", e)

		time.sleep(1)






def AWModuleMainF(squeue):
	global csv_files
	global bf
	global keyloggerp
	lastHwnd = ''
	process = ''
	while True:
		try:
			hwnd = win32gui.GetForegroundWindow()
			if hwnd != lastHwnd:
				bf = 0
				squeue.put(('ba',0))
				title = win32gui.GetWindowText(hwnd)

				for file in csv_files:
					print(file.split('\\')[-1], title)
					if title and isinstance(file, str) and file.split('\\')[-1] in title:
						logging('active window', 'Открыт охраняемый файл', 'Средний уровень угрозы')
						continue

				if "Открытие" in title:
					win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
					logging('active window', 'Открыл окно выгрузки файлов', 'Высокий уровень угрозы')
					continue
				pid = win32process.GetWindowThreadProcessId(hwnd)[1]
				try:
					process = psutil.Process(pid)
					if process.name() != 'chrome.exe':
						event = f'Активировано окно программы {process.name()}'
						logging('active window', event, 'Низкий уровень угрозы')

					if process.name() == 'chrome.exe':
						logging('active window', 'Открыл браузер', 'Средний уровень угрозы')
						squeue.put(('ba',1))
						bf = 1
						if keyloggerp == None:
							keyloggerp = threading.Thread(target=KLModuleMainF)
							keyloggerp.start()

				except psutil.NoSuchProcess:
					pass

				
				lastHwnd = hwnd

		except Exception as e:
			print("AW module: ",e)
		finally:
			pass


def CBModuleMainF(squeue):
	print('tcp gavno')
	last_clipboard_content = None
	while True:
		try:
			clipboard_content = None
			clipboard_type = None
			try:
				win32clipboard.OpenClipboard()
				clipboard_content = win32clipboard.GetClipboardData(win32con.CF_UNICODETEXT)
				clipboard_type = 'Text'
			except:
				clipboard_content = None
				clipboard_type = None
			finally:
				win32clipboard.CloseClipboard()

			files = get_clipboard_files()

			if files:
				clipboard_content = ', '.join(files)
				clipboard_type = 'File'
			if clipboard_content and clipboard_content != last_clipboard_content:
				squeue.put(('iincb',0))
				last_clipboard_content = clipboard_content
				if clipboard_type == 'File':
					for file in files:
						if vault in file:
							squeue.put(('iincb',1))
							logging('clipboard', 'Скопировал корпоративную информацию.', 'Средний уровень угрозы')
				if clipboard_type == 'Text':
					if csvCheckExpression(clipboard_content):
						squeue.put(('iincb',1))
						logging('clipboard', 'Скопировал корпоративную информацию.', 'Средний уровень угрозы')
			time.sleep(1)
		except Exception as e:
			print(e)
		finally:
			pass

def signalHandling(squeue):
	signals = {"iincb": 0, "ba": 0}
	while True:
		item = squeue.get()
		if item is None:
			continue
		key, value = item
		signals[key] = value
		print(signals)
		if signals["iincb"] == 1 and signals["ba"] == 1:
			signals = {"iincb": 0, "ba": 0}
			logging('clipboard','Скопировал корпоративные данные, открыто окно браузера','Высокий уровень угрозы')
			win32clipboard.OpenClipboard()
			win32clipboard.EmptyClipboard()
			win32clipboard.CloseClipboard()
		squeue.task_done()

def logSending(delay, client_socket):
	while True:
		time.sleep(delay)

		# lscb = os.path.getsize(LOG_CB)
		# lsaw = os.path.getsize(LOG_AW)
		# lskl = os.path.getsize(LOG_CB)
		# lsusb = os.path.getsize(LOG_CB)

		client_socket.sendall("SEND_LOG_CB".encode('utf-8'))
		# client_socket.sendall(str(lscb).encode("utf-8"))
		with open(LOG_CB, "rb") as file:
			while chunk := file.read(16 * 1024):
				client_socket.sendall(chunk)
		with open(LOG_CB, "w", encoding='utf-8') as file:
			file.truncate(0)

		time.sleep(2)

		client_socket.sendall("SEND_LOG_AW".encode('utf-8'))
		# client_socket.sendall(str(lsaw).encode("utf-8"))
		with open(LOG_AW, "rb") as file:
			while chunk := file.read(16 * 1024):
				client_socket.sendall(chunk)
		with open(LOG_AW, "w", encoding='utf-8') as file:
			file.truncate(0)

		time.sleep(2)

		client_socket.sendall("SEND_LOG_KL".encode('utf-8'))
		# client_socket.sendall(str(lskl).encode("utf-8"))
		with open(LOG_KL, "rb") as file:
			while chunk := file.read(16 * 1024):
				client_socket.sendall(chunk)
		with open(LOG_KL, "w", encoding='utf-8') as file:
			file.truncate(0)

		time.sleep(2)

		client_socket.sendall("SEND_LOG_USB".encode('utf-8'))
		# client_socket.sendall(str(lskl).encode("utf-8"))
		with open(LOG_USB, "rb") as file:
			while chunk := file.read(16 * 1024):
				client_socket.sendall(chunk)
		with open(LOG_USB, "w", encoding='utf-8') as file:
			file.truncate(0)

	# send_message(client_socket, "SEND_LOG_USB")
	# client_socket.sendall(str(file_size).encode("utf-8"))
	# with open(LOG_USB, "rb") as file:
	#     while chunk := file.read(16 * 1024):
	#         client_socket.sendall(chunk)

		# time.sleep(delay)

def clientProgram(client_socket):
	try:
		global vault

		exstnc(LOG_CB)
		exstnc(LOG_AW)
		exstnc(LOG_KL)
		exstnc(LOG_USB)

		client_socket.sendall("IDENTIFY".encode('utf-8'))
		client_socket.sendall(IDENTIFIER.encode('utf-8'))

		time.sleep(2)

		client_socket.sendall("GET_CONFIG".encode('utf-8'))
		config_data = json.loads(client_socket.recv(4096).decode('utf-8'))      
		delay = config_data.get("delay")
		vault = (config_data.get("vault")).format(IDENTIFIER)

		csvcheck()

		logSendingThread = threading.Thread(target=logSending, args=(delay,client_socket))#запустить поток с отправщиком логов
		logSendingThread.start()

		CBModule = threading.Thread(target=CBModuleMainF, args=(squeue,))
		CBModule.start()
		AWModule = threading.Thread(target=AWModuleMainF, args=(squeue,))
		AWModule.start()
		USBModule = threading.Thread(target=USBModuleMainF)
		USBModule.start()

		# logSendingThread.join()
	except Exception as e:
		print(f"An error occurred: {e}")
	finally:
		client_socket.close()




def serverListening():
	client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	client_socket.connect((SERVER_IP, SERVER_PORT))
	clientProgram(client_socket)



if __name__ == "__main__":

	squeue = queue.Queue()
	signalHandler = threading.Thread(target=signalHandling, args=(squeue,))
	signalHandler.start()

	serverListening()
