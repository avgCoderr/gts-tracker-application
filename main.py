import sys
import os
import glob
import json
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QDialog, QVBoxLayout, QLabel, QListWidget, QPushButton,
    QHBoxLayout, QMessageBox, QWidget, QListWidgetItem, QTextEdit
)

from dialog import ProjectDialog, EditProjectDialog, RouteLoggerDialog

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GPS Tracker Application - GTA")

        layout = QHBoxLayout()

        left_panel = QVBoxLayout()
        self.project_list = QListWidget()
        self.project_list.itemClicked.connect(self.load_project_details)
        
        self.route_list = []

        create_btn = QPushButton("Create New Project")
        create_btn.clicked.connect(self.create_project)

        left_panel.addWidget(QLabel("Projects"))
        left_panel.addWidget(self.project_list)
        left_panel.addWidget(create_btn)

        self.project_info = QLabel("Select a project to view details")
        self.project_info.setWordWrap(True)

        self.taxonomy_list = QListWidget()

        right_panel = QVBoxLayout()
        right_panel.addWidget(QLabel("Project Info"))
        right_panel.addWidget(self.project_info)
        right_panel.addWidget(QLabel("Taxonomy"))
        right_panel.addWidget(self.taxonomy_list)

        layout.addLayout(left_panel, 1)
        layout.addLayout(right_panel, 2)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.load_projects()

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def create_project(self):
        dialog = ProjectDialog(self)
        if dialog.exec_():
            name, freq, taxonomy = dialog.get_data()
            if name:
                project_data = {
                    "projectName": name,
                    "gpsFrequency": freq,
                    "taxonomy": taxonomy
                }

                os.makedirs("app_data/projects", exist_ok=True)
                project_path = os.path.join("app_data", "projects", f"{name}.json")

                with open(project_path, "w") as f:
                    json.dump(project_data, f, indent=2)
                    
                QMessageBox.information(self, "Project Created", f"Name: {name}\nGPS Frequency: {freq}s")
                self.refresh_project_list()
            else:
                QMessageBox.warning(self, "Invalid Input", "Project name cannot be empty.")
                
    def load_projects(self):
        self.project_list.clear()
        project_dir = os.path.join("app_data", "projects")
        os.makedirs(project_dir, exist_ok=True)
        for filename in os.listdir(project_dir):
            if filename.endswith(".json"):
                item = QListWidgetItem(filename)
                item.setData(1000, os.path.join(project_dir, filename))
                self.project_list.addItem(item)

    def load_project_details(self, item):
        project_file = item.data(1000)
        try:
            with open(project_file, "r") as f:
                data = json.load(f)

            name = data.get("projectName", "N/A")
            freq = data.get("gpsFrequency", "N/A")
            taxonomy = data.get("taxonomy", [])

            self.project_info.setText(f"Name: {name}\nGPS Frequency: {freq}s")

            self.taxonomy_list.clear()
            for entry in taxonomy:
                class_name = entry.get("className", "Unknown")
                attrs = ", ".join(entry.get("attributes", []))
                self.taxonomy_list.addItem(f"{class_name} → {attrs}")

            if hasattr(self, "edit_btn"):
                self.edit_btn.deleteLater()
            if hasattr(self, "log_btn"):
                self.log_btn.deleteLater()
            if hasattr(self, "log_view_btn"):
                self.log_view_btn.deleteLater()

            self.edit_btn = QPushButton("Edit This Project")
            self.edit_btn.clicked.connect(lambda: self.edit_project(project_file))
            self.centralWidget().layout().itemAt(1).layout().addWidget(self.edit_btn)
            
            self.log_btn = QPushButton("Start Route Logging")
            self.log_btn.clicked.connect(lambda: self.open_route_logger(data, project_file))
            self.centralWidget().layout().itemAt(1).layout().addWidget(self.log_btn)
            
            self.log_view_btn = QPushButton("Check Route Logs")
            self.log_view_btn.clicked.connect(lambda: self.open_route_logs(data, project_file))
            self.centralWidget().layout().itemAt(1).layout().addWidget(self.log_view_btn)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load project: {e}")

    def open_route_logs(self, project_data, project_path):
        project_name = project_data['projectName']
        route_dir = os.path.join("app_data", "routes")
        route_files = glob.glob(os.path.join(route_dir, f"route_{project_name}_*.jsonl"))

        if not route_files:
            QMessageBox.information(self, "No Routes", f"No route logs found for project: {project_name}")
            return

        dialog = QDialog(self)
        dialog.setWindowTitle(f"Routes for {project_name}")
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Click a route to view logs:"))

        for route_file in sorted(route_files, reverse=True):  # Show latest first
            filename = os.path.basename(route_file)
            btn = QPushButton(filename)
            btn.clicked.connect(lambda _, f=route_file: self.show_route_logs(f))
            layout.addWidget(btn)

        dialog.setLayout(layout)
        dialog.exec_()
        
    def show_route_logs(self, filepath):
        viewer = QDialog(self)
        viewer.setWindowTitle(f"Log View – {os.path.basename(filepath)}")
        layout = QVBoxLayout()

        text_edit = QTextEdit()
        text_edit.setReadOnly(True)

        # Load and pretty print first 50 lines
        lines = []
        with open(filepath, "r") as f:
            for i, line in enumerate(f):
                if i >= 50:
                    lines.append("...\n(Only showing first 50 logs)")
                    break
                try:
                    lines.append(json.dumps(json.loads(line), indent=2))
                except json.JSONDecodeError:
                    lines.append(line)

        text_edit.setText("\n\n".join(lines))
        layout.addWidget(text_edit)

        viewer.setLayout(layout)
        viewer.resize(600, 500)
        viewer.exec_()
    
    def open_route_logger(self, project_data, project_path):
        dlg = RouteLoggerDialog(self, project_data, project_path)
        dlg.exec_()
        
    def edit_project(self, project_path):
        dialog = EditProjectDialog(self, project_path=project_path)
        if dialog.exec_():
            QMessageBox.information(self, "Updated", "Project updated successfully.")
            self.refresh_project_list()
            
    def refresh_project_list(self):
        self.load_projects()
        self.project_info.setText("Select a project to view details")
        self.taxonomy_list.clear()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(800, 400)
    window.show()
    sys.exit(app.exec_())
