import sys

from PyQt5.QtWidgets import QApplication
from .ui import MainWindow

if __name__ == '__main__':
    app = QApplication(sys.argv)

    # Create a Qt widget, which will be our window.
    window = MainWindow()
    window.show()  # IMPORTANT!!!!! Windows are hidden by default.

    # Start the event loop.
    sys.exit(app.exec())
