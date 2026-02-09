from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QLabel,
    QComboBox,
    QPushButton,
)
from PySide6.QtCore import Qt
import sys

from ui.replay_launcher import start_replay


class Dashboard(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("F1 Telemetry Replay — Dashboard")
        self.setFixedSize(400, 300)

        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setAlignment(Qt.AlignCenter)

        # ================= TITLE =================
        title = QLabel("F1 Telemetry Replay")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)

        # ================= CIRCUIT =================
        circuit_label = QLabel("Select Circuit / Location")
        layout.addWidget(circuit_label)

        self.circuit_dropdown = QComboBox()
        self.circuit_dropdown.addItems([
            "Monza",
            "Silverstone",
            "Spa",
            "Suzuka",
        ])
        layout.addWidget(self.circuit_dropdown)

        # ================= TEAM =================
        team_label = QLabel("Select Team")
        layout.addWidget(team_label)

        self.team_dropdown = QComboBox()
        self.team_dropdown.addItems([
            "ALL",
            "Ferrari",
            "Red Bull",
            "Mercedes",
        ])
        layout.addWidget(self.team_dropdown)

        # ================= START BUTTON =================
        self.start_button = QPushButton("Start Replay")
        self.start_button.setFixedHeight(36)
        self.start_button.clicked.connect(self.on_start_clicked)
        layout.addWidget(self.start_button)

        self.setLayout(layout)

    # ================= CLICK HANDLER =================
    def on_start_clicked(self):
        circuit = self.circuit_dropdown.currentText()
        team = self.team_dropdown.currentText()

        self.close()  # VERY IMPORTANT

        start_replay(circuit=circuit, team=team)


# ================= APP ENTRY =================
def run_dashboard():
    app = QApplication(sys.argv)
    window = Dashboard()
    window.show()
    sys.exit(app.exec())
