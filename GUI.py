import sys
import subprocess
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QProgressBar, QTextEdit, QLabel


class Worker(QThread):
    """A worker thread to run the Python program"""
    finished = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.process = None

    def run(self):
        self.process = subprocess.Popen(['python', 'Program.py'])
        self.process.wait()
        self.finished.emit()

    def stop(self):
        if self.process is not None:
            self.process.terminate()


class ModelGenWorker(QThread):
    """A worker thread to run the ModelGen programs"""
    finished = pyqtSignal(str)

    def __init__(self, program):
        super().__init__()
        self.process = None
        self.program = program

    def run(self):
        self.process = subprocess.Popen(['python', self.program], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = self.process.communicate()
        self.finished.emit(stdout.decode() + '\n' + stderr.decode())

    def stop(self):
        if self.process is not None:
            self.process.terminate()


class App(QWidget):
    def __init__(self):
        super().__init__()
        self.title = 'Data Predictor'
        self.left = 200
        self.top = 200
        self.width = 320
        self.height = 350
        self.worker = None
        self.modelgen_worker = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        # create the Run button
        run_btn = QPushButton('Run', self)
        run_btn.setToolTip('Run the program')
        run_btn.clicked.connect(self.run_program)

        # create the Stop button
        stop_btn = QPushButton('Stop', self)
        stop_btn.setToolTip('Stop the program')
        stop_btn.clicked.connect(self.stop_program)

        # create the Auto Update Model button
        auto_update_btn = QPushButton('Model Update - Auto', self)
        auto_update_btn.setToolTip('Run ModelGen_Direct.py')
        auto_update_btn.clicked.connect(self.run_modelgen_direct)

        # create the Custom Model Update button
        custom_update_btn = QPushButton('Model Update - Custom', self)
        custom_update_btn.setToolTip('Run ModelGen_CustomData.py')
        custom_update_btn.clicked.connect(self.run_modelgen_custom)

        # create the Quit button
        quit_btn = QPushButton('Quit', self)
        quit_btn.setToolTip('Quit the program')
        quit_btn.clicked.connect(self.quit_program)

        # create the layout and add buttons to it
        layout = QVBoxLayout(self)
        layout.addWidget(run_btn)
        layout.addWidget(stop_btn)
        layout.addWidget(auto_update_btn)
        layout.addWidget(custom_update_btn)
        layout.addWidget(quit_btn)

        # create the progress bar
        self.progress_bar = QProgressBar(self)
        layout.addWidget(self.progress_bar)

        # create the text box for ModelGen output
        self.modelgen_output = QTextEdit(self)
        layout.addWidget(self.modelgen_output)

        # create the labels for additional text
        auto_update_label = QLabel("Auto: Atualiza o modelo de previsão com base nos últimos 1000 valores guardados no Adafruit IO", self)
        custom_update_label = QLabel("Custom: Atualiza o modelo de previsão com base em ficheiros CSV obtidos manualmente (Será necessário mudar as diretorias dos datasets no ficheiro ModelGen_CustomData.py)", self)

        # add the labels to the layout
        layout.addWidget(auto_update_label)
        layout.addWidget(custom_update_label)

        self.show()

    def run_program(self):
        # start the worker thread to run the Python program
        self.worker = Worker()
        self.worker.finished.connect(self.on_worker_finished)
        self.worker.start()

        # start the progress bar animation
        self.progress_bar.setRange(0, 0)

    def stop_program(self):
        # stop the worker thread if it's running
        if self.worker is not None:
            self.worker.stop()

        # reset the progress bar
        self.progress_bar.setRange(0, 1)
        self.progress_bar.setValue(0)

    def on_worker_finished(self):
        # reset the progress bar
        self.progress_bar.setRange(0, 1)
        self.progress_bar.setValue(0)

    def run_modelgen_direct(self):
        # start the ModelGen worker thread to run ModelGen_Direct.py
        self.modelgen_worker = ModelGenWorker('ModelGen_Direct.py')
        self.modelgen_worker.finished.connect(self.on_modelgen_finished)
        self.modelgen_worker.start()

    def run_modelgen_custom(self):
        # start the ModelGen worker thread to run ModelGen_CustomData.py
        self.modelgen_worker = ModelGenWorker('ModelGen_CustomData.py')
        self.modelgen_worker.finished.connect(self.on_modelgen_finished)
        self.modelgen_worker.start()

    def on_modelgen_finished(self, output):
        # display the output of ModelGen in the text box
        self.modelgen_output.append(output)

    def quit_program(self):
        # stop the worker thread if it's running
        if self.worker is not None:
            self.worker.stop()
        if self.modelgen_worker is not None:
            self.modelgen_worker.stop()
        sys.exit()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
