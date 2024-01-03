from PyQt5.QtCore import QAbstractTableModel, Qt, QTimer
from PyQt5.QtWidgets import (
    QProgressDialog, )

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


class UpdateDataQProgressDialog:

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
        eid, group_code = self._eid_data[self.steps]

        hotel_data = self._cc.get_Regulate_Hotel(groupEID=eid)
        log_data = self._cc.get_RegulateLogList(groupEID=eid)
        dd = ly_lib.comp_hotel_data(ly_lib.parser_hotel_data(hotel_data),
                                    ly_lib.parser_loglist(log_data))
        dd = [{"团号": group_code, **d} for d in dd]
        self.parent._cache_data = [*self.parent._cache_data, *dd]
        self.steps += 1

        return

    def cancel(self):
        self.t.stop()
        return
