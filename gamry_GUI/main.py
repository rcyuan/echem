import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit,
    QVBoxLayout, QFormLayout, QPushButton, QMessageBox
)
from PySide6.QtCore import Qt

class GamryConfigWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gamry Experiment Configuration")
        self.setMinimumWidth(300)

        # Create input fields with default values
        self.init_freq_input = QLineEdit("100000")  # 100 kHz
        self.final_freq_input = QLineEdit("1")      # 1 Hz
        self.ac_voltage_input = QLineEdit("0.01")   # 10 mV
        self.dc_voltage_input = QLineEdit("0.0")    # 0 V
        self.ppd_input = QLineEdit("10")            # 10 points per decade

        # Form layout
        form_layout = QFormLayout()
        form_layout.addRow("Initial Frequency (Hz):", self.init_freq_input)
        form_layout.addRow("Final Frequency (Hz):", self.final_freq_input)
        form_layout.addRow("AC Voltage (V):", self.ac_voltage_input)
        form_layout.addRow("DC Voltage (V):", self.dc_voltage_input)
        form_layout.addRow("Points per Decade:", self.ppd_input)

        # Submit button
        self.submit_btn = QPushButton("Run")
        self.submit_btn.clicked.connect(self.run_experiment)

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.addLayout(form_layout)
        main_layout.addWidget(self.submit_btn, alignment=Qt.AlignmentFlag.AlignRight)
        self.setLayout(main_layout)

    def run_experiment(self):
        # Grab and validate values
        try:
            init_freq = float(self.init_freq_input.text())
            final_freq = float(self.final_freq_input.text())
            ac_voltage = float(self.ac_voltage_input.text())
            dc_voltage = float(self.dc_voltage_input.text())
            ppd = int(self.ppd_input.text())

            # Show values for now — this is where you'd call your script
            msg = (
                f"Running experiment with:\n"
                f"Initial Freq: {init_freq} Hz\n"
                f"Final Freq: {final_freq} Hz\n"
                f"AC Voltage: {ac_voltage} V\n"
                f"DC Voltage: {dc_voltage} V\n"
                f"Points/Decade: {ppd}"
            )
            QMessageBox.information(self, "Parameters Submitted", msg)
        except ValueError:
            QMessageBox.critical(self, "Input Error", "Please enter valid numeric values.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GamryConfigWindow()
    window.show()
    sys.exit(app.exec())
