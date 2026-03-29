import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QLabel,
    QComboBox,
    QPushButton,
)
from PySide6.QtCore import Qt

from ui.replay_launcher import start_replay
from ui.circuits import CIRCUIT_MAP


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

        # Load circuits dynamically from CIRCUIT_MAP
        self.circuit_options = list(CIRCUIT_MAP.keys())
        self.circuit_dropdown.addItems(self.circuit_options)

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
            "McLaren",
            "Aston Martin",
            "Alpine",
            "Williams",
            "RB",
            "Haas",
            "Sauber",
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

        self.close()  # Close dashboard before launching replay

        start_replay(circuit=circuit, team=team)


# ================= APP ENTRY =================
def run_dashboard():
    app = QApplication(sys.argv)
    window = Dashboard()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    run_dashboard()
