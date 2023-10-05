import json
import pandas as pd
from PyQt5.QtCore import QSize, QAbstractTableModel, Qt, QTimer
from PyQt5.QtWidgets import (QComboBox, QDateTimeEdit, QErrorMessage, QMainWindow,
                              QMessageBox, QPushButton, QWidget,
                             QVBoxLayout, QHBoxLayout, QLineEdit, QFormLayout,
                             QSizePolicy, QTableView, QProgressDialog,)
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

        self.pd = QProgressDialog("解析网站数据", "取消数据解析", 0, len(data), self.parent)
        self.pd.canceled.connect(self.cancel)
        self.steps = 0
        self.t =  QTimer(self.parent)
        self.t.timeout.connect(self.perform)
        self.t.start(0)

        return

    def exec(self):
        return self.pd.exec()

    def perform(self):
        print(self.parent.xx)
        self.pd.setValue(self.steps)
        eid = self._eid_data[self.steps]
        hotel_data = self._cc.get_Regulate_Hotel(groupEID=eid)
        log_data = self._cc.get_RegulateLogList(groupEID=eid)
        dd = ly_lib.comp_hotel_data(ly_lib.parser_hotel_data(hotel_data),
                                    ly_lib.parser_loglist(log_data))
        self.parent._cache_data=[]
        self.parent._cache_data = [*self.parent._cache_data, *dd]
        self.steps += 1
        if self.steps > self.pd.maximum():
            self.t.stop()

            self.parent.xx += 3
            return

    def cancel(self):
        self.t.stop()
        #.. cleanup
        return


class MainWindow(QMainWindow):
    _cache_data_file = "./lyouoa_data.json"

    def __init__(self):
        super().__init__()

        self.setMinimumSize(QSize(800, 600))
        #self.setFixedSize(QSize(800, 600))
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

        # time
        self.start_time_edit = QDateTimeEdit(self)
        self.end_time_edit = QDateTimeEdit(self)

        # owner
        self.owner_edit = QComboBox()
        # type
        self.room_type_edit = QComboBox()
        self.room_type_edit.insertItems(0, ["标准", "司陪"])

        # parser data
        self.refresh_data_button = QPushButton("刷新数据")
        self.refresh_data_button.clicked.connect(self.refresh_data)

        self.filter_data_button = QPushButton("过滤数据")
        self.filter_data_button.clicked.connect(self.filter_data)

        self.export_data_button = QPushButton("导出数据")
        #self.export_data_button.clicked.connect(self.show_progress_dialo)

        login_option_layout = QFormLayout()
        login_option_layout.addRow("系统地址:", self.host_edit)
        login_option_layout.addRow("公司代码:", self.comp_code_edit)
        login_option_layout.addRow("会话ID:", self.session_id_edit)

        filter_option_layout = QFormLayout()
        filter_option_layout.addRow("开始时间:", self.start_time_edit)
        filter_option_layout.addRow("结束时间:", self.end_time_edit)
        filter_option_layout.addRow("姓名:", self.owner_edit)
        filter_option_layout.addRow("房间类型:", self.room_type_edit)

        action_layout = QFormLayout()
        action_layout.addWidget(self.refresh_data_button)
        action_layout.addWidget(self.filter_data_button)
        action_layout.addWidget(self.export_data_button)

        loayout = QHBoxLayout()
        loayout.setSpacing(10)
        loayout.addLayout(login_option_layout)
        loayout.addLayout(filter_option_layout)
        loayout.addLayout(action_layout)

        w = QWidget()
        w.setLayout(loayout)
        w.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        #w.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        return w

    def reload_cache(self):

        try:
            self.data = pd.read_json(self._cache_data_file)
        except Exception as e:
            self.show_error_message(str(e))
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
        self.owner_edit.addItems(list(set(ower_data.to_list())))
        return

    def update_room_type(self):
        if len(self.data) == 0:
            return
        room_type_data = self.data["房间类型"]
        self.room_type_edit.clear()
        self.room_type_edit.addItems(list(set(room_type_data.to_list())))
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
            count = cc.get_eid_count()
            data = cc.get_tanhao(limit=count)
            print(count, len(data))

            pg = UpdateDataQProgressDialog(self, cc, data[:100])
            pg.exec()

            if len(self._cache_data) > 0:
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
        ower = self.data["ower"]
        select_ower = self.owner_edit.currentText()
        if len(select_ower) == 0:
            self._filtered_data = self.data
            return
        self._filtered_data = self.data[ower == select_ower]
        return

    def filter_data(self):
        print(self.owner_edit.currentText())
        self.update_filter_data()
        self.set_table_model()

        return
