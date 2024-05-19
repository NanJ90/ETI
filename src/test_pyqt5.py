from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel

app = QApplication([])
window = QMainWindow()
window.setWindowTitle('PyQt5 Test')
label = QLabel('PyQt5 is working!', parent=window)
label.move(50, 50)
window.setGeometry(100, 100, 200, 100)
window.show()
app.exec_()
