# path: main.py

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QComboBox, QPushButton, QLabel, QFileDialog
from Configuration import Configuration
from scheduler import solve_backtracking, solve_simulated_annealing

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Schedule Solver")
        self.setGeometry(100, 100, 400, 300)
        
        self.config = Configuration.GetInstance()
        self.config_file = ""

        layout = QVBoxLayout()
        
        self.label = QLabel("Select Algorithm:", self)
        layout.addWidget(self.label)
        
        self.comboBox = QComboBox(self)
        self.comboBox.addItem("Backtracking with Simulated Annealing")
        layout.addWidget(self.comboBox)
        
        self.loadButton = QPushButton("Load Configuration File", self)
        self.loadButton.clicked.connect(self.load_configuration_file)
        layout.addWidget(self.loadButton)
        
        self.runButton = QPushButton("Run Solver", self)
        self.runButton.clicked.connect(self.run_solver)
        layout.addWidget(self.runButton)
        
        self.resultLabel = QLabel("", self)
        layout.addWidget(self.resultLabel)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def load_configuration_file(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Configuration File", "", "All Files (*);;Text Files (*.txt)", options=options)
        if file_name:
            self.config_file = file_name
            self.config.Parsefile(self.config_file)
            self.resultLabel.setText(f"Loaded configuration from: {file_name}")

    def run_solver(self):
        if not self.config_file:
            self.resultLabel.setText("Please load a configuration file first.")
            return
        
        algorithm = self.comboBox.currentText()
        result = None
        
        if algorithm == "Backtracking with Simulated Annealing":
            result = solve_backtracking(self.config)
        
        if result:
            self.resultLabel.setText(f"Result: {result}")
        else:
            self.resultLabel.setText("No valid schedule found.")

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
