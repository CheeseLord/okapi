from canvas import Canvas

from PyQt5 import QtWidgets


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    win = QtWidgets.QMainWindow()

    c = Canvas()
    win.setCentralWidget(c)

    win.show()
    app.instance().exec_()

