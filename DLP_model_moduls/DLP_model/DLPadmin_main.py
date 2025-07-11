    # This Python file uses the following encoding: utf-8
import os
from pathlib import Path
import sys

import socket
import threading
import json
import csv

from PySide6.QtWidgets import QApplication, QWidget, QListWidgetItem, QTableWidget, QTableWidgetItem, QPushButton
from PySide6.QtCore import QFile
from PySide6.QtUiTools import QUiLoader
from PySide6.QtGui import QColor

#возможно сделать подгрузку ip с json файла или вернуть получение адреса через функцию

CONFIG_FILE = "C:\\Users\\Admin\\DLP\\conf.json"
#CLIENT_CACHE_FILE = "C:\\Users\\Admin\\DLP\\conf.json"
CLIENT_CACHE_FILE = "C:\\Users\\Admin\\DLP\\client_cache.json"
#CLIENT_CACHE_FILE = "C:\\Users\\Admin\\DLP\\client_cache.json"

SERVER_IP = "192.168.30.11"
#server_ip = socket.gethostbyname(socket.gethostname())
SERVER_PORT = 6001

clients = {}

def showAction(text, color = QColor(0, 0, 0)):
    item = QListWidgetItem(text)
    item.setForeground(color)
    widget.pl.addItem(item)

def clrefresh():
    with open(CLIENT_CACHE_FILE, "w") as json_file:
        json.dump(clients, json_file)
    widget.cl.setRowCount(len(clients))
    i = 0
    for ip, values in clients.items():
        name, status = values
        item = QTableWidgetItem("{}({})".format(ip, name))
        if(status == 0):
            color = QColor(255, 0, 0)
        elif(status == 1):
            color = QColor(0,128,0)
        item.setForeground(color)
        widget.cl.setItem(i, 0, item)
        i += 1

def lvrefresh():#функция по кнопке обновляющая list widget; внутри нее запуск функции анализа логов искусственным интеллектом
    data_list = []
    with open(f"C:\\Users\\Admin\\DLP\\log_cb_{client_address[0]}.csv", "r", encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            data_list.append(row)
        for log_entry in data_list:
            item = QListWidgetItem(log_entry)
            widget.cbl.addItem(item)

    data_list = []
    with open(f"C:\\Users\\Admin\\DLP\\log_aw_{client_address[0]}.csv", "r", encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            data_list.append(row)
        for log_entry in data_list:
            item = QListWidgetItem(log_entry)
            widget.awl.addItem(item)

    data_list = []
    with open(f"C:\\Users\\Admin\\DLP\\log_kl_{client_address[0]}.csv", "r", encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            data_list.append(row)
        for log_entry in data_list:
            item = QListWidgetItem(log_entry)
            widget.kll.addItem(item)

    data_list = []
    with open(f"C:\\Users\\Admin\\DLP\\log_usb_{client_address[0]}.csv", "r", encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            data_list.append(row)
        for log_entry in data_list:
            item = QListWidgetItem(log_entry)
            widget.usbl.addItem(item)


def client_handling(client_socket, client_address):
    print("handling start")
    showAction("Успешное соединение с {}.".format(client_address),QColor(0, 128, 0))
    if client_address[0] not in clients:
        clients[client_address[0]] = ["Unknown", 1]
    else:
        clients[client_address[0]][1] = 1
    clrefresh()

    try:
        while True:
            message = client_socket.recv(1024).decode("utf-8")

            if message == "IDENTIFY":
                identifier = client_socket.recv(1024).decode("utf-8")
                clients[client_address[0]][0] = identifier

                showAction("{} представился как {}.".format(client_address[0],identifier),QColor(0, 128, 0))
                clrefresh()

            elif message == "GET_CONFIG":
                showAction("{}({}) запросил файл конфигурации.".format(clients[client_address[0]],client_address[0]),QColor(0, 128, 0))

                with open(CONFIG_FILE, "r") as config_file:
                    config_data = config_file.read()
                client_socket.sendall(config_data.encode("utf-8"))
                showAction("Файл конфигурации отправлен клиенту {}({}).".format(clients[client_address[0]],client_address[0]),QColor(0, 128, 0))

            elif message == "SEND_LOG_CB":
                showAction("{}({}) отправляет журнал буфера обмена.".format(clients[client_address[0]],client_address[0]),QColor(0, 128, 0))

                received_data = b""
                received_data = client_socket.recv(16 * 1024)
                received_data = b'\n' + received_data
                file_path = "C:\\Users\\Admin\\DLP\\log_cb_{client_address[0]}.csv"
                if not os.path.exists(file_path):
                    with open(file_path, "w", encoding='utf-8') as log_file:
                        log_file.write('Timestamp,User,Module,Event,Mark\n')
                with open(file_path, "ab") as log_file:
                    log_file.write(received_data)

                showAction("Принят журнал буфера обмена от {}({}).".format(clients[client_address[0]],client_address[0]),QColor(0, 128, 0))

            elif message == "SEND_LOG_AW":
                showAction("{}({}) отправляет журнал активности окон.".format(clients[client_address[0]],client_address[0]),QColor(0, 128, 0))

                received_data = b""
                # while len(received_data) < file_size:
                received_data = client_socket.recv(16 * 1024)
                received_data = b'\n' + received_data
                file_path = "C:\\Users\\Admin\\DLP\\log_aw_{client_address[0]}.csv"
                if not os.path.exists(file_path):
                    with open(file_path, "w", encoding='utf-8') as log_file:
                        log_file.write('Timestamp,User,Module,Event,Mark\n')
                with open(file_path, "ab") as log_file:
                    log_file.write(received_data)

                showAction("Принят журнал активности окон от {}({}).".format(clients[client_address[0]],client_address[0]),QColor(0, 128, 0))

            elif message == "SEND_LOG_KL":
                showAction("{}({}) отправляет журнал буфера обмена.".format(clients[client_address[0]],client_address[0]),QColor(0, 128, 0))

                received_data = b""
                # while len(received_data) < file_size:
                received_data = client_socket.recv(16 * 1024)
                received_data = b'\n' + received_data
                file_path = "C:\\Users\\Admin\\DLP\\log_kl_{client_address[0]}.csv"
                if not os.path.exists(file_path):
                    with open(file_path, "w", encoding='utf-8') as log_file:
                        log_file.write('Timestamp,User,Module,Event,Mark\n')
                with open(file_path, "ab") as log_file:
                    log_file.write(received_data)

                showAction("Принят журнал кей-логера от {}({}).".format(clients[client_address[0]],client_address[0]),QColor(0, 128, 0))

            elif message == "SEND_LOG_USB":
                showAction("{}({}) отправляет журнал подключаемых USB-хранилищ.".format(clients[client_address[0]],client_address[0]),QColor(0, 128, 0))

                received_data = b""
                # while len(received_data) < file_size:
                received_data += client_socket.recv(16 * 1024)
                received_data = b'\n' + received_data
                file_path = "C:\\Users\\Admin\\DLP\\log_usb_{client_address[0]}.csv"
                if not os.path.exists(file_path):
                    with open(file_path, "w", encoding='utf-8') as log_file:
                        log_file.write('Timestamp,User,Module,Event,Mark\n')
                with open(file_path, "ab", encoding='utf-8') as log_file:
                    log_file.write(received_data)

                showAction("Принят журнал подключаемых USB-хранилищ от {}({}).".format(clients[client_address[0]],client_address[0]),QColor(0, 128, 0))

            elif message == "DISCONNECT":
                showAction("{}({}) послал запрос о прекращении соединения.".format(clients[client_address[0]][0],client_address[0]))
                break

    except Exception as e:
        print(e)
        showAction("Ошибка при обработке клиента {}: {}".format(client_address[0], e),QColor(255, 0, 0))
    finally:
        clients[client_address[0]][1] = 0
        clrefresh()
        client_socket.close()
        showAction("Соединение с {}({}) разорвано.".format(clients[client_address[0]][0],client_address[0]))


def start_server():
    server_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    server_socket.bind((SERVER_IP, SERVER_PORT))
    server_socket.listen(5)

    showAction("Сервер запущен на {}:{}.".format(SERVER_IP, SERVER_PORT),QColor(0, 128, 0))

    while True:
        print(1)
        client_socket, client_address = server_socket.accept()
        print(f"Incoming connection from {client_address}")
        client_thread = threading.Thread(target=client_handling, args=(client_socket, client_address))
        print("Thread created, starting thread...")
        client_thread.start()
        print("Thread started")


class Gui(QWidget):
    def __init__(self):
        super(Gui, self).__init__()
        self.load_ui()

    def load_ui(self):
        loader = QUiLoader()
        path = os.fspath(Path(__file__).resolve().parent / "form.ui")
        ui_file = QFile(path)
        ui_file.open(QFile.ReadOnly)
        loader.load(ui_file, self)
        ui_file.close()
        self.setWindowTitle("DLP Admin")

        self.pl = self.findChild(QWidget, "pl") #вывод процессов
        self.cl = self.findChild(QWidget, "cl") #таблица клиентов
        self.cbl = self.findChild(QWidget, "cbl")#выводы логов
        self.awl = self.findChild(QWidget, "awl")
        self.kll = self.findChild(QWidget, "kll")
        self.usbl = self.findChild(QWidget, "usbl")
        self.rb = self.findChild(QWidget, "rb")#кнопка обновления
        #вывод ии

        self.cl.setColumnCount(1)
        self.cl.setHorizontalHeaderItem(0, QTableWidgetItem("Список клиентов:"))
        self.cl.setColumnWidth(0, 250)

        self.rb.clicked.connect(self.rbclicked)

    def rbclicked(self):
        lvrefresh()





if __name__ == "__main__":
    app = QApplication([])
    widget = Gui()
    widget.show()

    widget.pl.addItem("Hi!")

    if os.path.exists(CLIENT_CACHE_FILE):
        showAction("Найден файл базы клиентов.",QColor(0, 128, 0))
        with open(CLIENT_CACHE_FILE, "r", encoding='utf-8') as json_file:
            showAction("Загрузка базы клиентов.",QColor(0, 128, 0))
            clients = json.load(json_file)
        clrefresh()

    else:
        showAction("Файл базы клиентов не найден.",QColor(150, 150, 0))

    server_thread = threading.Thread(target=start_server)
    server_thread.start()

    sys.exit(app.exec())
