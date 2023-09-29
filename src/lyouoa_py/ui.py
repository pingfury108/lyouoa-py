import pandas as pd
from PyQt5.QtCore import QSize, QAbstractTableModel, Qt
from PyQt5.QtWidgets import (QComboBox, QDateTimeEdit, QMainWindow,
                             QMessageBox, QPushButton, QWidget,
                             QVBoxLayout, QHBoxLayout, QLineEdit, QFormLayout,
                             QSizePolicy, QTableView)
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


class MainWindow(QMainWindow):

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
        self.owner_edit.insertItems(1, ["张三", "李四"])
        self.owner_edit.insertItems(0, ["王五", "想想"])

        # type
        self.room_type_edit = QComboBox()
        self.room_type_edit.insertItems(0, ["标准", "司陪"])

        # parser data
        self.refresh_data_button = QPushButton("刷新数据")
        self.refresh_data_button.clicked.connect(self.refresh_data)
        self.filter_data_button = QPushButton("过滤数据")
        self.export_data_button = QPushButton("导出数据")

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

    @property
    def data_show_ui(self, ) -> QWidget:
        loayout = QVBoxLayout()
        self.table = QTableView()

        self.data = pd.DataFrame()

        self.model = TableModel(self.data)
        self.table.setModel(self.model)
        loayout.addWidget(self.table)
        w = QWidget()
        w.setLayout(loayout)
        w.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        return w

    def refresh_data(self, ):
        print("refresh")
        cc = ly_lib.LyouoaClient(host=self.host_edit.text(),
                                 session_id=self.session_id_edit.text(),
                                 company_code=self.comp_code_edit.text())
        msg = QMessageBox()
        msg.setText("数据刷新成功")
        try:
            count = cc.get_eid_count()
            data = cc.get_tanhao(limit=count)
            print(count, len(data))
            self.table.setModel(TableModel(pd.DataFrame(data, columns=["EID"])))
        except ly_lib.LyouoaException as e:
            msg.setText(str(e))

        msg.exec()
        return
