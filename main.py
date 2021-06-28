from PyQt5 import QtWidgets


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    win = QtWidgets.QMainWindow()

    b = QtWidgets.QPushButton('Click Me!')
    win.setCentralWidget(b)

    win.show()
    app.instance().exec_()

