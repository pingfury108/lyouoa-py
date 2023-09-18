from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import (QMainWindow, QWidget, QPushButton, QVBoxLayout,
                             QHBoxLayout, QLineEdit, QFormLayout)


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setMinimumSize(QSize(800, 600))
        #self.setFixedSize(QSize(800, 600))
        self.setWindowTitle("loyouoa 数据统计")
        # loayout
        main_loayout = QHBoxLayout()
        main_loayout.addWidget(self.login_ui)
        main_loayout.addWidget(self.data_show_ui)
        main_loayout.addWidget(self.option_ui)
        # Set the central widget of the Window.
        widget = QWidget()
        widget.setLayout(main_loayout)
        self.setCentralWidget(widget)

        return

    @property
    def login_ui(self, ) -> QWidget:

        # system address
        host_edit = QLineEdit()
        host_edit.setText("https://vip.lyouoa.com")
        host_edit.textChanged.connect(self.host_changed)

        # Company code
        comp_code_edit = QLineEdit()
        comp_code_edit.textChanged.connect(self.comp_code_changed)

        # http client session id
        session_id_edit = QLineEdit()
        session_id_edit.textChanged.connect(self.client_session_changed)

        formLayout = QFormLayout()
        formLayout.addRow("系统地址:", host_edit)
        formLayout.addRow("公司代码:", comp_code_edit)
        formLayout.addRow("会话ID:", session_id_edit)

        loayout = QVBoxLayout()
        loayout.addLayout(formLayout)

        w = QWidget()
        w.setLayout(loayout)

        return w

    def host_changed(self, t):
        self.host = t

        return

    def comp_code_changed(self, t):
        self.company_code = t

        return

    def client_session_changed(self, t):
        self.client_session = t

        return

    @property
    def data_show_ui(self, ) -> QWidget:
        loayout = QVBoxLayout()
        loayout.addWidget(QPushButton("data show, 1, Press Me!"))
        loayout.addWidget(QPushButton("middle, 2, Press Me!"))
        w = QWidget()
        w.setLayout(loayout)

        return w

    @property
    def option_ui(self, ) -> QWidget:
        loayout = QVBoxLayout()
        loayout.addWidget(QPushButton("option, 1, Press Me!"))
        loayout.addWidget(QPushButton("right, 2, Press Me!"))

        w = QWidget()
        w.setLayout(loayout)

        return w
