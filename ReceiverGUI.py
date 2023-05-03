from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QApplication
from PyQt5 import QtCore, QtWidgets
import sys

from utils import logger
from Receiver import Receiver

class ReceiverGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.__receiver_memory = ""
        self.__connection = False

        self.__width = 300
        self.__height = 350

        self.__setup_GUI()

        self.__receiver = Receiver()
        self.__receiver.sig_update_receiver.connect(self.__update_receiver)
        self.__receiver.sig_handle_event.connect(self.__handle_event)

    def __setup_GUI(self):

        self.setWindowTitle("Receiver - UDP")
        self.setGeometry(1000, 50, self.__width, self.__height)

        self.__set_conn()
        self.__set_checkbox()
        self.__set_receive()

        self.__toggle_GUI()

    def __set_IP(self):

        self.__lbIP = QtWidgets.QLabel(self)
        self.__lbIP.setGeometry(QtCore.QRect(60, 20, 100, 15))
        self.__lbIP.setObjectName("lbIP")
        self.__lbIP.setText("Group IP")
        self.__lbIP.setEnabled(False)

        self.__teIP = QtWidgets.QTextEdit(self)
        self.__teIP.setGeometry(QtCore.QRect(60, 40, 100, 30))
        self.__teIP.setObjectName("teIP")
        self.__teIP.setPlaceholderText("224.1.1.1")
        self.__teIP.setText("224.1.1.1")
        self.__teIP.setEnabled(False)

    def __set_port(self):

        self.__lbPort = QtWidgets.QLabel(self)
        self.__lbPort.setGeometry(QtCore.QRect(60, 75, 100, 15))
        self.__lbPort.setObjectName("lbPort")
        self.__lbPort.setText("Conn Port")

        self.__tePort = QtWidgets.QTextEdit(self)
        self.__tePort.setGeometry(QtCore.QRect(60, 95, 100, 30))
        self.__tePort.setObjectName("tePort")
        self.__tePort.setPlaceholderText("5000")
        self.__tePort.setText("5000")

    def __set_checkbox(self):
        self.__cbMulticast = QtWidgets.QCheckBox(self)
        self.__cbMulticast.setGeometry(QtCore.QRect(60, 130, 90, 25))
        self.__cbMulticast.setObjectName("cbMulticast")
        self.__cbMulticast.setText("Multicast")
        self.__cbMulticast.clicked.connect(self.__switch_mode)

    def __set_conn(self):

        self.__set_IP()
        self.__set_port()

        self.__btnConn = QtWidgets.QPushButton(self)
        self.__btnConn.setGeometry(QtCore.QRect(60, 160, 100, 25))
        self.__btnConn.setObjectName("btnConn")
        self.__btnConn.setText("Connect")
        self.__btnConn.clicked.connect(self.__connect)

        self.__btnDisconn = QtWidgets.QPushButton(self)
        self.__btnDisconn.setGeometry(QtCore.QRect(60, 190, 100, 25))
        self.__btnDisconn.setObjectName("btnDisconn")
        self.__btnDisconn.setText("Disconnect")
        self.__btnDisconn.clicked.connect(self.__disconnect)

    def __set_receive(self):

        self.__lbReceive = QtWidgets.QLabel(self)
        self.__lbReceive.setGeometry(QtCore.QRect(60, 220, 100, 15))
        self.__lbReceive.setObjectName("lbReceive")
        self.__lbReceive.setText("Received text")
        self.__lbReceive.setDisabled(True)

        self.__teReceive = QtWidgets.QTextEdit(self)
        self.__teReceive.setGeometry(QtCore.QRect(60, 240, 200, 100))
        self.__teReceive.setObjectName("teReceive")
        self.__teReceive.setReadOnly(True)
        self.__teReceive.setDisabled(True)

    def __toggle_GUI(self) -> None:
        self.__lbReceive.setEnabled(self.__connection)
        self.__teReceive.setEnabled(self.__connection)
        self.__lbPort.setEnabled(not self.__connection)
        self.__tePort.setEnabled(not self.__connection)
        self.__cbMulticast.setEnabled(not self.__connection)

        if self.__cbMulticast.isChecked():
            self.__lbIP.setEnabled(not self.__connection)
            self.__teIP.setEnabled(not self.__connection)

        self.__btnConn.setEnabled(not self.__connection)
        self.__btnDisconn.setEnabled(self.__connection)

        self.__receiver_memory = ""
        self.__teReceive.setText(self.__receiver_memory)

    def __show_popup(self, title: str = 'Info', msg: str = '', retry: bool = True) -> None:
        popup = QMessageBox(self)
        popup.setWindowTitle(title)
        popup.setText(msg)
        if retry:
            popup.setStandardButtons(QMessageBox.Retry | QMessageBox.Ok)
            popup.setDefaultButton(QMessageBox.Retry)
        else: popup.setStandardButtons(QMessageBox.Ok)
        popup.exec_()
        if popup.standardButton(popup.clickedButton()) == QMessageBox.Retry:
            self.__connect()

    def __connect(self):
        logger.info("Called connect method")
        ip = self.__teIP.toPlainText()
        port = self.__tePort.toPlainText()
        msg = self.__receiver.connect(group_ip=ip, conn_port=port, multicast=self.__cbMulticast.isChecked())
        if msg is not None: self.__show_popup(msg=msg)
        else:
            self.__connection = True
            self.__toggle_GUI()

    def __switch_mode(self):
        self.__lbIP.setEnabled(self.__cbMulticast.isChecked())
        self.__teIP.setEnabled(self.__cbMulticast.isChecked())

    def __disconnect(self):
        logger.info("Called disconnect method")
        self.__receiver.disconnect()
        self.__connection = False
        self.__toggle_GUI()

    def __send(self):
        msg = self.__teSend.toPlainText()
        self.__receiver.send(msg)
        self.__teSend.setText("")  # clear QTextEdit after send

    @pyqtSlot(str, bool)
    def __handle_event(self, msg: str, retry=False):
        logger.info(msg)
        self.__disconnect()
        self.__show_popup(msg=msg, retry=retry)

    @pyqtSlot(str)
    def __update_receiver(self, msg: str):
        self.__receiver_memory += msg + '\n'
        self.__teReceive.setText(self.__receiver_memory)
        self.__teReceive.verticalScrollBar().setValue(self.__teReceive.verticalScrollBar().maximum())

    def closeEvent(self, event) -> None:
        ''' close app by X '''
        if self.__receiver.get_connection_status():
            self.__receiver.disconnect()
        QApplication.quit()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ReceiverGUI()
    window.show()
    sys.exit(app.exec_())
