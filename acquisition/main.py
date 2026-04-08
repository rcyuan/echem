from PySide2.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QFormLayout, QVBoxLayout, QPushButton
)
import sys
import sys
sys.path.append(r"C:\Program Files (x86)\Gamry Instruments\Python37-32\Lib\site-packages")
import toolkitpy as tkp



class GamryControlGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gamry Control Panel")
        self.init_ui()

    def init_ui(self):
        # Form layout for parameters
        form_layout = QFormLayout()

        self.freq_start_input = QLineEdit("1")  # Default: 1 Hz
        self.freq_end_input = QLineEdit("100000")  # Default: 100 kHz
        self.ac_voltage_input = QLineEdit("0.01")  # Default: 10 mV
        self.dc_voltage_input = QLineEdit("0.0")   # Default: 0 V
        self.ppd_input = QLineEdit("10")           # Default: 10 points/decade

        form_layout.addRow("Initial Frequency (Hz):", self.freq_start_input)
        form_layout.addRow("Final Frequency (Hz):", self.freq_end_input)
        form_layout.addRow("AC Voltage (V):", self.ac_voltage_input)
        form_layout.addRow("DC Voltage (V):", self.dc_voltage_input)
        form_layout.addRow("Points per Decade:", self.ppd_input)

        # Run button
        run_button = QPushButton("Run Experiment")
        run_button.clicked.connect(self.run_experiment)

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.addLayout(form_layout)
        main_layout.addWidget(run_button)

        self.setLayout(main_layout)

    def run_experiment(self):
        # For now, just print the parameter values
        print("Starting Experiment with parameters:")
        print("Initial Frequency:", self.freq_start_input.text())
        print("Final Frequency:", self.freq_end_input.text())
        print("AC Voltage:", self.ac_voltage_input.text())
        print("DC Voltage:", self.dc_voltage_input.text())
        print("Points per Decade:", self.ppd_input.text())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GamryControlGUI()
    window.show()
    sys.exit(app.exec_())
