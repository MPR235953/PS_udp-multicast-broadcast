import socket
import struct
import threading

import utils
from utils import logger
from PyQt5.QtCore import pyqtSignal, QObject

class Receiver(QObject):
    sig_update_receiver = pyqtSignal(str)
    sig_handle_event = pyqtSignal(str, bool)
    def __init__(self):
        super().__init__()
        self.__group_ip = None
        self.__conn_port = None
        self.__receiver_socket = None
        self.__listener = None
        self.__connection = False
        self.__is_multicast = False

    def get_connection_status(self):
        return self.__connection

    def connect(self, group_ip: str, conn_port: str, multicast: bool) -> str:
        try:
            logger.info("Set up web stuff")
            self.__group_ip = group_ip
            self.__conn_port = int(conn_port)
            self.__is_multicast = multicast

            self.__receiver_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)  # Enable UDP
            self.__receiver_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Enable reusing address

            if self.__is_multicast:
                mreq = struct.pack("4sl", socket.inet_aton(self.__group_ip), socket.INADDR_ANY)
                self.__receiver_socket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
                self.__receiver_socket.bind((self.__group_ip, self.__conn_port))
            else:
                self.__receiver_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)  # Enable broadcasting mode
                self.__receiver_socket.bind(("", self.__conn_port))  # bind

            self.__connection = True
            self.__listener = threading.Thread(target=self.__listen)
            self.__listener.start()

            logger.info("Start listening")
        except Exception as e: return str(e)

    def disconnect(self):
        self.__connection = False
        if self.__is_multicast: self.__receiver_socket.sendto(str.encode(utils.CLIENT_DISCONNECT_KEY), (self.__group_ip, self.__conn_port))
        else: self.__receiver_socket.sendto(str.encode(utils.CLIENT_DISCONNECT_KEY), ('<broadcast>', self.__conn_port))
        self.__receiver_socket.close()
        logger.info("Disconnected")

    def __listen(self):
        logger.info("listening ...")
        while self.__connection:
            try:
                recv, addr = self.__receiver_socket.recvfrom(utils.CONFIG['max_transfer'])
                recv_len = len(recv)
                if str(recv.decode("utf-8")) == utils.CLIENT_DISCONNECT_KEY: continue
                if recv_len > 0:
                    self.sig_update_receiver.emit(str(recv.decode("utf-8")) + ' - {} bytes'.format(recv_len))
                else: break
            except Exception as e:
                break
        logger.info("Listener task was finished")
