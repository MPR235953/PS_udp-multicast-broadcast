import socket

import utils
from utils import logger
from PyQt5.QtCore import pyqtSignal, QObject

class Transmitter(QObject):
    sig_handle_event = pyqtSignal(str, bool)
    def __init__(self):
        super().__init__()
        self.__group_ip = None
        self.__conn_port = None
        self.__transmitter_socket = None
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

            self.__transmitter_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)  # Enable UDP
            self.__transmitter_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)  # Enable reusing address

            if self.__is_multicast:
                self.__transmitter_socket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
            else:
                self.__transmitter_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)  # Enable broadcasting mode

            self.__connection = True

        except Exception as e: return str(e)

    def disconnect(self):
        self.__connection = False
        if self.__is_multicast: self.__transmitter_socket.sendto(str.encode(utils.CLIENT_DISCONNECT_KEY), (self.__group_ip, self.__conn_port))
        else: self.__transmitter_socket.sendto(str.encode(utils.CLIENT_DISCONNECT_KEY), ('<broadcast>', self.__conn_port))
        self.__transmitter_socket.close()
        logger.info("Disconnected")

    def send(self, msg: str):
        if self.__is_multicast: self.__transmitter_socket.sendto(str.encode(msg), (self.__group_ip, self.__conn_port))
        else: self.__transmitter_socket.sendto(str.encode(msg), ('<broadcast>', self.__conn_port))
        logger.info("Message was sent")
