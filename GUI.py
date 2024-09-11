import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QLineEdit, QPushButton, QTextEdit, QWidget, QMessageBox
from PyQt5.QtCore import QThread, pyqtSignal
import subprocess

class ScraperThread(QThread):
    log_signal = pyqtSignal(str)

    def __init__(self, search, total):
        super().__init__()
        self.search = search
        self.total = total

    def run(self):
        try:
            self.log_signal.emit("Starting scraping...\n")
            # Call the original script 'main.py'
            cmd = ['python', 'main.py', '-s', self.search, '-t', str(self.total)]
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

            # Capture the output and errors
            for line in process.stdout:
                self.log_signal.emit(line)
            for line in process.stderr:
                self.log_signal.emit(line)
            process.wait()

            self.log_signal.emit("Scraping completed!\n")
        except Exception as e:
            self.log_signal.emit(f"Error: {str(e)}\n")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Google Maps Scraper GUI")

        layout = QVBoxLayout()

        # Search Query
        self.search_label = QLabel("Search Query:")
        layout.addWidget(self.search_label)
        self.search_input = QLineEdit()
        layout.addWidget(self.search_input)

        # Total Results
        self.total_label = QLabel("Total Results:")
        layout.addWidget(self.total_label)
        self.total_input = QLineEdit()
        layout.addWidget(self.total_input)

        # Start Button
        self.start_button = QPushButton("Start Scraping")
        self.start_button.clicked.connect(self.start_scraping)
        layout.addWidget(self.start_button)

        # Log Output
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        layout.addWidget(self.log_output)

        # Set central widget
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def start_scraping(self):
        search = self.search_input.text()
        total = self.total_input.text()

        if not search or not total:
            QMessageBox.warning(self, "Input Error", "Please provide both a search query and total results.")
            return

        try:
            total = int(total)
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Total results must be a valid integer.")
            return

        self.thread = ScraperThread(search, total)
        self.thread.log_signal.connect(self.update_log)
        self.thread.start()

    def update_log(self, log_message):
        self.log_output.append(log_message)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
