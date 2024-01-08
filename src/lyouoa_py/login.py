import httpx

from urllib.parse import urljoin
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import (
    QDialog,
    QErrorMessage,
    QLabel,
    QPushButton,
    QLineEdit,
    QFormLayout,
)


class LoginDilog(QDialog):
    accepted = pyqtSignal()

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        self.user_name_edit = QLineEdit()
        self.user_pwd_edit = QLineEdit()
        self.user_pwd_edit.setEchoMode(QLineEdit.Password)
        self.validate_code_edit = QLineEdit()
        self.btn = QPushButton("登录")
        # self.btn.setDisabled(True)
        self.btn.clicked.connect(self.ok_pressed)

        self.user_agent = "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0"

        self.session_key = "ASP.NET_SessionId"
        self.cookies = httpx.Cookies()
        if self.parent.session_id_edit.text().strip() != "":
            self.cookies.set(self.session_key,
                             self.parent.session_id_edit.text())
        #
        form = QFormLayout(self)
        form.addRow("账号:", self.user_name_edit)
        form.addRow("密码", self.user_pwd_edit)
        form.addRow("验证码:", self.validate_code_edit)
        form.addWidget(self.show_login_validate_code())
        form.addRow(self.btn)
        return

    def show_login_validate_code(self):
        label = QLabel()
        #
        try:
            r = httpx.get(url=urljoin(self.parent.host_edit.text(),
                                      "GetValidateCode?Height=40"),
                          headers={"User-Agent": self.user_agent},
                          cookies=self.cookies)
            if r.status_code == 200:
                if self.cookies.get(self.session_key, "").strip() == "":
                    session_id = r.cookies.get(self.session_key, "")
                    self.cookies.set(self.session_key, session_id)
                    self.parent.session_id_edit.setText(session_id)

                #
                image = QImage()
                image.loadFromData(r.content)
                label.setPixmap(QPixmap(image))

            else:
                self.show_message(r.text)
        except Exception as e:
            self.show_error_message(str(e))

        #
        return label

    def show_error_message(self, text: str):
        msg = QErrorMessage(self)
        msg.showMessage(text)
        msg.exec()
        return

    def unlock(self, text):
        if text:
            self.btn.setEnabled(True)
        else:
            self.btn.setDisabled(True)

        return

    def ok_pressed(self):
        try:
            r = httpx.post(
                url=urljoin(self.parent.host_edit.text(), "/LoginAuth"),
                headers={"User-Agent": self.user_agent},
                cookies=self.cookies,
                data={
                    "userid": self.user_name_edit.text(),
                    "password": self.user_pwd_edit.text(),
                    "companyuid": self.parent.comp_code_edit.text(),
                    "verifycode": self.validate_code_edit.text(),
                },
            )
            if r.status_code != 200:
                self.show_error_message(r.text)

            #
            if not r.json().get("IsSuccess", False):
                self.show_error_message(r.json().get("Msg", ""))
            else:
                rl = httpx.get(r.json().get("Data"),
                               cookies=self.cookies,
                               follow_redirects=True)
                if rl.status_code != 200:
                    self.show_error_message(r.text)

                #
                self.parent.usercode = self.user_name_edit.text()

                #
                self.accepted.emit()
                self.accept()
        except Exception as e:
            self.show_error_message(str(e))

            return
