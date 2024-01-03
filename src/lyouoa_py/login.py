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
        super().__init__(*args, **kwargs)
        self.parent = parent
        self.user_name_edit = QLineEdit()
        self.user_pwd_edit = QLineEdit()
        self.user_pwd_edit.setEchoMode(QLineEdit.Password)
        self.validate_code_edit = QLineEdit()
        self.btn = QPushButton("登录")
        # self.btn.setDisabled(True)
        self.btn.clicked.connect(self.ok_pressed)

        form = QFormLayout(self)
        form.addRow("账号:", self.user_name_edit)
        form.addRow("密码", self.user_pwd_edit)
        form.addRow("验证码:", self.validate_code_edit)
        form.addWidget(self.show_login_validate_code())
        form.addRow(self.btn)
        return

    def show_login_validate_code(self):
        label = QLabel()
        try:
            r = httpx.get(
                "https://www.lyouoa.com/GetValidateCode?Height=40",
                headers={
                    "User-Agent":
                    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
                },
                cookies={
                    "companyuid": self.parent.comp_code_edit.text(),
                    "usercode": self.user_name_edit.text(),
                    "companyuid_sso": "",
                },
            )
            if r.status_code == 200:
                print(r.cookies)
                self.parent.session_id_edit.setText(
                    r.cookies.get("ASP.NET_SessionId", ""))
                image = QImage()
                image.loadFromData(r.content)
                label.setPixmap(QPixmap(image))
            else:
                self.show_message(r.text)
        except Exception as e:
            self.show_error_message(str(e))

        return label

    def show_error_message(self, text: str):
        msg = QErrorMessage()
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
                headers={
                    "Referer":
                    "http://vip.lyouoa.com/default?",
                    "Accept":
                    "application/json, text/javascript, */*; q=0.01",
                    "Origin":
                    "http://vip.lyouoa.com",
                    "X-Requested-With":
                    "XMLHttpRequest",
                    "Content-Type":
                    "application/x-www-form-urlencoded; charset=UTF-8",
                    "User-Agent":
                    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
                },
                cookies={
                    "ASP.NET_SessionId": self.parent.session_id_edit.text(),
                    "companyuid": self.parent.comp_code_edit.text(),
                    "usercode": self.user_name_edit.text(),
                    "companyuid_sso": "",
                },
                data={
                    "userid": self.user_name_edit.text(),
                    "password": self.user_pwd_edit.text(),
                    "ompanyuid": self.parent.comp_code_edit.text(),
                    "verifycode": self.validate_code_edit.text(),
                },
            )
            print(r.request)
            print(r.request.headers)
            print(r.request.content)
            print(r.status_code, r.text)
            print(r.cookies)
            if r.status_code != 200:
                self.show_error_message(r.text)

            #
            self.accepted.emit({})
            self.accept()
        except Exception as e:
            self.show_error_message(str(e))

        return
