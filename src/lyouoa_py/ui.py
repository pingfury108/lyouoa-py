import json
from PyQt5.QtGui import QImage, QPixmap
import httpx
import pandas as pd
from PyQt5.QtCore import QDate, QSize, QAbstractTableModel, Qt, QTimer, pyqtSignal
from PyQt5.QtWidgets import (
    QComboBox,
    QDateEdit,
    QDialog,
    QErrorMessage,
    QFileDialog,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QFormLayout,
    QSizePolicy,
    QTableView,
    QProgressDialog,
)
import lyouoa_py.lib as ly_lib


class TableModel(QAbstractTableModel):

    def __init__(self, data):
        super(TableModel, self).__init__()
        self._data = data
        return

    def data(self, index, role):
        if role == Qt.DisplayRole:
            value = self._data.iloc[index.row(), index.column()]
            return str(value)

    def rowCount(self, index):
        return self._data.shape[0]

    def columnCount(self, index):
        return self._data.shape[1]

    def headerData(self, section, orientation, role):
        # section is the index of the column/row.
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return str(self._data.columns[section])

            if orientation == Qt.Vertical:
                return str(self._data.index[section])
        return


class UpdateDataQProgressDialog():

    def __init__(self, parent, cc: ly_lib.LyouoaClient, data: list) -> None:
        self.parent = parent
        self._eid_data = data
        self._cc = cc
        self.parent._cache_data = []

        self.pd = QProgressDialog("正在解析网站数据", "取消", 0, len(data), self.parent)
        self.pd.setFixedWidth(400)
        self.pd.canceled.connect(self.cancel)
        self.steps = 0
        self.t = QTimer(self.parent)
        self.t.timeout.connect(self.perform)
        self.t.start(0)

        return

    def exec(self):
        return self.pd.exec()

    def perform(self):
        self.pd.setValue(self.steps)
        if self.steps >= self.pd.maximum():
            self.t.stop()
            return
        eid = self._eid_data[self.steps]

        start_time = str(self.parent.start_time_edit.date().toPyDate())
        end_time = str(self.parent.end_time_edit.date().toPyDate())
        print(start_time, end_time)

        hotel_data = self._cc.get_Regulate_Hotel(groupEID=eid,
                                                 start_time=start_time,
                                                 end_time=end_time)
        log_data = self._cc.get_RegulateLogList(groupEID=eid)
        dd = ly_lib.comp_hotel_data(ly_lib.parser_hotel_data(hotel_data),
                                    ly_lib.parser_loglist(log_data))
        self.parent._cache_data = [*self.parent._cache_data, *dd]
        self.steps += 1

        return

    def cancel(self):
        self.t.stop()
        return


class LoginDilog(QDialog):
    accepted = pyqtSignal(dict)

    def __init__(self, parent, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.parent = parent
        self.user_name_edit = QLineEdit()
        self.user_pwd_edit = QLineEdit()
        self.user_pwd_edit.setEchoMode(QLineEdit.Password)
        self.validate_code_edit = QLineEdit()
        self.btn = QPushButton('OK')
        #self.btn.setDisabled(True)
        self.btn.clicked.connect(self.ok_pressed)

        form = QFormLayout(self)
        form.addRow('账号:', self.user_name_edit)
        form.addRow('密码', self.user_pwd_edit)
        form.addRow('验证码:', self.validate_code_edit)
        form.addWidget(self.show_login_validate_code())
        form.addRow(self.btn)
        return

    def show_login_validate_code(self):
        label = QLabel()
        try:
            r = httpx.get("https://www.lyouoa.com/GetValidateCode?Height=40")
            if r.status_code == 200:
                image = QImage()
                image.loadFromData(r.content)
                label.setPixmap(QPixmap(image))
            else:
                self.show_message(r.text)
        except Exception as e:
            self.show_error_message(str(e))

        return label

    def unlock(self, text):
        if text:
            self.btn.setEnabled(True)
        else:
            self.btn.setDisabled(True)

        return

    def ok_pressed(self):
        values = {
            'host': self.parent.host_edit.text(),
            'comp': self.parent.comp_code_edit.text(),
            'user_name': self.user_name_edit.text(),
            'user_pwd': self.user_pwd_edit.text(),
            'validate_code': self.validate_code_edit.text()
        }
        self.accepted.emit(values)
        self.accept()
        return


class MainWindow(QMainWindow):
    _cache_data_file = "./lyouoa_data.json"

    def __init__(self):
        super().__init__()

        #self.setMinimumSize(QSize(1000, 800))
        self.setFixedSize(QSize(800, 600))
        self.setWindowTitle("loyouoa 数据统计")
        # layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.option_ui)
        # data layout
        main_layout.addWidget(self.data_show_ui)
        # Set the central widget of the Window.
        widget = QWidget()
        widget.setLayout(main_layout)

        self.setCentralWidget(widget)

        return

    @property
    def option_ui(self, ) -> QWidget:

        # system address
        self.host_edit = QLineEdit()
        self.host_edit.setText("https://vip.lyouoa.com")

        # Company code
        self.comp_code_edit = QLineEdit()
        self.comp_code_edit.setText("366820")

        # http client session id
        self.session_id_edit = QLineEdit()

        # login, name ValidateCode
        self.login_button = QPushButton("登录&&获取会话ID")
        self.login_button.clicked.connect(self.login)

        # time
        self.start_time_edit = QDateEdit(self)
        self.start_time_edit.setMinimumDate(QDate(2022, 1, 1))
        self.start_time_edit.setDisplayFormat("yyyy-MM-dd")

        self.end_time_edit = QDateEdit()
        self.end_time_edit.setMinimumDate(QDate(2023, 1, 1))
        self.end_time_edit.setDisplayFormat("yyyy-MM-dd")
        #self.end_time_edit.setDisplayFormat("2023-1-1")

        # owner
        self.owner_edit = QComboBox()
        # type
        self.room_type_edit = QComboBox()

        # parser data
        self.refresh_data_button = QPushButton("刷新数据")
        self.refresh_data_button.clicked.connect(self.refresh_data)

        self.filter_data_button = QPushButton("过滤数据")
        self.filter_data_button.clicked.connect(self.filter_data)

        self.export_data_button = QPushButton("导出数据")
        self.export_data_button.clicked.connect(self.export_data)

        self.analyze_info_button = QPushButton("显示统计信息")
        self.analyze_info_button.clicked.connect(self.analyze_info)

        login_option_layout = QFormLayout()
        login_option_layout.addRow("系统地址:", self.host_edit)
        login_option_layout.addRow("公司代码:", self.comp_code_edit)
        login_option_layout.addRow("会话ID:", self.session_id_edit)
        login_option_layout.addWidget(self.login_button)

        fetch_layout = QFormLayout()
        fetch_layout.addRow("开始时间:", self.start_time_edit)
        fetch_layout.addRow("结束时间:", self.end_time_edit)
        fetch_layout.addWidget(self.refresh_data_button)

        filter_option_layout = QFormLayout()
        filter_option_layout.addRow("姓名:", self.owner_edit)
        filter_option_layout.addRow("房间类型:", self.room_type_edit)
        filter_option_layout.addWidget(self.filter_data_button)
        filter_option_layout.addWidget(self.export_data_button)

        analyze_layout = QFormLayout()
        analyze_layout.addWidget(self.analyze_info_button)

        loayout = QHBoxLayout()
        loayout.setSpacing(10)
        loayout.addLayout(login_option_layout)
        loayout.addLayout(fetch_layout)
        loayout.addLayout(filter_option_layout)
        loayout.addLayout(analyze_layout)

        w = QWidget()
        w.setLayout(loayout)
        w.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        #w.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        return w

    def login(self):
        print("login")
        dilog = LoginDilog(self)
        dilog.accepted.connect(
            lambda values: self.session_id_edit.setText(str(values)))
        dilog.exec()

        return

    def reload_cache(self):

        try:
            self.data = pd.read_json(self._cache_data_file)
        except Exception as e:
            #self.show_error_message(str(e))
            self.data = pd.DataFrame()

        self.update_owners()
        self.update_room_type()
        self.update_filter_data()
        return

    def update_owners(self):
        if len(self.data) == 0:
            return
        ower_data = self.data["ower"]
        self.owner_edit.clear()
        self.owner_edit.addItems(["-", *list(set(ower_data.to_list()))])
        return

    def update_room_type(self):
        if len(self.data) == 0:
            return
        room_type_data = self.data["房间类型"]
        self.room_type_edit.clear()
        self.room_type_edit.addItems(
            ["-", *list(set(room_type_data.to_list()))])
        return

    @property
    def data_show_ui(self, ) -> QWidget:
        self.reload_cache()
        loayout = QVBoxLayout()
        self.table = QTableView()
        self.model = TableModel(pd.DataFrame(self._filtered_data))
        self.table.setModel(self.model)
        loayout.addWidget(self.table)
        w = QWidget()
        w.setLayout(loayout)
        w.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        return w

    def set_table_model(self):
        self.table.setModel(TableModel(pd.DataFrame(self._filtered_data)))

        return

    def refresh_data(self, ):
        cc = ly_lib.LyouoaClient(host=self.host_edit.text(),
                                 session_id=self.session_id_edit.text(),
                                 company_code=self.comp_code_edit.text())
        try:
            start_time = str(self.start_time_edit.date().toPyDate())
            end_time = str(self.end_time_edit.date().toPyDate())
            print(start_time, end_time)
            count = cc.get_eid_count()
            data = cc.get_tanhao(limit=count,
                                 start_time=start_time,
                                 end_time=end_time)
            print(count)

            pg = UpdateDataQProgressDialog(self, cc, data)
            pg.exec()

            if len(self._cache_data) > 0:
                print(len(self._cache_data))
                self.data = pd.DataFrame(self._cache_data)
                with open(self._cache_data_file, 'w') as f:
                    json.dump(self._cache_data, f)
                    self.update_owners()
                    self.update_room_type()
                    self.filter_data()
                    self.show_message(text="数据刷新成功")
            else:
                self.show_message(text="无刷新")
        except ly_lib.LyouoaException as e:
            self.show_error_message(text=str(e))

    def show_message(self, text: str):
        msg = QMessageBox()
        msg.setText(text)
        msg.exec()
        return

    def show_error_message(self, text: str):
        msg = QErrorMessage()
        msg.showMessage(text)
        msg.exec()
        return

    def update_filter_data(self):
        if len(self.data) == 0:
            self._filtered_data = self.data
            return
        select_ower = self.owner_edit.currentText()
        if select_ower != "-":
            dd = self.data[self.data["ower"] == select_ower]
            select_room_type = self.room_type_edit.currentText()
            if select_room_type != "-":
                self._filtered_data = dd[dd["房间类型"] ==
                                         self.room_type_edit.currentText()]
            else:
                self._filtered_data = dd
        else:
            select_room_type = self.room_type_edit.currentText()
            if select_room_type != "-":
                self._filtered_data = self.data[
                    self.data["房间类型"] == self.room_type_edit.currentText()]
            else:
                self._filtered_data = self.data
        return

    def filter_data(self):
        self.update_filter_data()
        self.set_table_model()

        return

    def analyze_info(self):
        msg = QMessageBox()
        if len(self._filtered_data) > 0:
            gby_data = self._filtered_data.groupby(["ower",
                                                    "房间类型"])[["房间数"]].sum()
            msg.setText(gby_data.to_html())
        else:
            msg.setText("没有数据")

        msg.exec()

        return

    def export_data(self):
        file, check = QFileDialog.getSaveFileName(
            self, "选择导出为的文件", "", "Microsoft Excel 2007-(*.xlsx);;",
            "Microsoft Excel 2007-(*.xlsx)")
        if check:
            try:
                if file:
                    self._filtered_data.to_excel(file)
            except Exception as e:
                self.show_error_message(str(e))
