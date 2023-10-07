import sys

from PyQt5.QtWidgets import QApplication
from lyouoa_py.ui import MainWindow


def run_ui():
    app = QApplication(sys.argv)
    app.setApplicationName("lyouoa-py")
    app.setApplicationVersion("v0.0.1")

    # Create a Qt widget, which will be our window.
    window = MainWindow()
    window.show()  # IMPORTANT!!!!! Windows are hidden by default.

    # Start the event loop.
    sys.exit(app.exec_())
