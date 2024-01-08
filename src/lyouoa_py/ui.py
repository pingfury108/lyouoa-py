import json
import pandas as pd

from PyQt5.QtCore import QDate, QSize
from PyQt5.QtWidgets import (
    QComboBox,
    QDateEdit,
    QErrorMessage,
    QFileDialog,
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
)

import lyouoa_py.lib as ly_lib
from lyouoa_py.login import LoginDilog
from lyouoa_py.widget import TableModel, UpdateDataQProgressDialog


class MainWindow(QMainWindow):
    _cache_data_file = "./lyouoa_data.json"

    def __init__(self):
        super().__init__()

        self.setMinimumSize(QSize(800, 600))
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
        self.host_edit.setText("http://vip.lyouoa.com")

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
        # self.end_time_edit.setDisplayFormat("2023-1-1")

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

        return w

    def login(self):
        dilog = LoginDilog(self)
        dilog.exec()

        return

    def reload_cache(self):
        try:
            self.data = pd.read_json(self._cache_data_file)
        except Exception as e:
            # self.show_error_message(str(e))
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
        self.owner_edit.addItems(sorted(["-",
                                         *list(set(ower_data.to_list()))]))
        return

    def update_room_type(self):
        if len(self.data) == 0:
            return
        room_type_data = self.data["房间类型"]
        self.room_type_edit.clear()
        self.room_type_edit.addItems(
            sorted(["-", *list(set(room_type_data.to_list()))]))
        return

    @property
    def data_show_ui(self, ) -> QWidget:
        self.reload_cache()
        loayout = QVBoxLayout()
        self.table = QTableView()
        self.model = TableModel(self._filtered_data)
        self.table.setModel(self.model)
        loayout.addWidget(self.table)
        w = QWidget()
        w.setLayout(loayout)
        w.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        return w

    def set_table_model(self):
        self.table.setModel(TableModel(self._filtered_data))

        return

    def refresh_data(self, ):
        cc = ly_lib.LyouoaClient(
            host=self.host_edit.text(),
            session_id=self.session_id_edit.text(),
            company_code=self.comp_code_edit.text(),
            usercode=self.usercode,
        )
        try:
            count = cc.get_eid_count(
                start_time=self.start_time_edit.text(),
                end_time=self.end_time_edit.text(),
            )
            data = cc.get_tanhao(
                start_time=self.start_time_edit.text(),
                end_time=self.end_time_edit.text(),
                count=count,
            )

            pg = UpdateDataQProgressDialog(self, cc, data)
            pg.exec()

            if len(self._cache_data) > 0:
                self.data = pd.DataFrame()
                self.data = pd.DataFrame(self._cache_data)
                with open(self._cache_data_file, "w") as f:
                    json.dump(self._cache_data, f)
                    self.update_owners()
                    self.update_room_type()
                    self.filter_data()
                    self.show_message(
                        text=f"数据刷新成功,共{len(self._cache_data)}条数据.")
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
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("统计信息")
        msg.setFixedSize(400, 200)
        if len(self._filtered_data) > 0:
            total = self._filtered_data["房间数"].sum()
            gby_data = self._filtered_data.groupby(["ower",
                                                    "房间类型"])[["房间数"]].sum()
            no_sipei_data = self._filtered_data[self._filtered_data["房间类型"] !=
                                                "司陪"]
            no_sipei_total = no_sipei_data["房间数"].sum()
            msg.setText(f"""<p>房间总数: { total }</p>
                <p>房间总数(不含司陪): {no_sipei_total}</p>
            汇总: { gby_data.to_html()}""")
        else:
            msg.setText("没有数据")

        msg.exec()

        return

    def export_data(self):
        file, check = QFileDialog.getSaveFileName(
            self,
            "选择导出为的文件",
            "",
            "Microsoft Excel 2007-(*.xlsx);;",
            "Microsoft Excel 2007-(*.xlsx)",
        )
        if check:
            try:
                if file:
                    self._filtered_data.to_excel(file)
            except Exception as e:
                self.show_error_message(str(e))
