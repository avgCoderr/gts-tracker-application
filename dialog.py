import os
import json
import time
from random import random

from PyQt5.QtWidgets import (
    QFormLayout, QDialog, QVBoxLayout, QLabel, QListWidget, QPushButton, QLineEdit,
    QHBoxLayout, QMessageBox, QDialogButtonBox, QInputDialog
)

from PyQt5.QtGui import QIntValidator
from PyQt5.QtCore import QTimer

class ProjectDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create Project")
        self.setMinimumWidth(400)

        self.name_input = QLineEdit()
        self.freq_input = QLineEdit()
        self.freq_input.setPlaceholderText("e.g., 10 (seconds)")
        self.freq_input.setValidator(QIntValidator(5, 20))
        self.freq_input.setToolTip("Enter GPS frequency between 5 and 20 seconds")

        self.taxonomy = []
        self.tax_class_input = QLineEdit()
        self.tax_class_input.setPlaceholderText("Enter Name of Class")
        self.tax_attr_input = QLineEdit()
        self.tax_attr_input.setPlaceholderText("Comma-separated (e.g., Sunny, Cloudy)")

        self.tax_list = QListWidget()

        form_layout = QFormLayout()
        form_layout.addRow("Project Name:", self.name_input)
        form_layout.addRow("GPS Frequency (sec):", self.freq_input)

        tax_layout = QVBoxLayout()
        tax_form = QHBoxLayout()
        tax_form.addWidget(self.tax_class_input)
        tax_form.addWidget(self.tax_attr_input)

        add_class_btn = QPushButton("Add Class")
        add_class_btn.clicked.connect(self.add_taxonomy_class)

        tax_layout.addLayout(tax_form)
        tax_layout.addWidget(add_class_btn)
        tax_layout.addWidget(self.tax_list)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addLayout(form_layout)
        layout.addSpacing(10)
        layout.addWidget(QLabel("Taxonomy (Class → Attributes):"))
        layout.addLayout(tax_layout)
        layout.addWidget(button_box)
        self.setLayout(layout)

    def add_taxonomy_class(self):
        class_name = self.tax_class_input.text().strip()
        attrs = [a.strip() for a in self.tax_attr_input.text().split(",") if a.strip()]
        if class_name and attrs:
            self.taxonomy.append({
                "className": class_name,
                "attributes": attrs
            })
            self.tax_list.addItem(f"{class_name}: {', '.join(attrs)}")
            self.tax_class_input.clear()
            self.tax_attr_input.clear()

    def accept(self):
        name = self.name_input.text().strip()
        freq_text = self.freq_input.text().strip()

        if not name:
            QMessageBox.warning(self, "Validation Error", "Project name cannot be empty.")
            return

        if not freq_text.isdigit():
            QMessageBox.warning(self, "Validation Error", "GPS frequency must be a number.")
            return

        freq = int(freq_text)
        if not (5 <= freq <= 20):
            QMessageBox.warning(self, "Validation Error", "GPS frequency must be between 5 and 20 seconds.")
            return

        super().accept()

    def get_data(self):
        return self.name_input.text().strip(), int(self.freq_input.text()), self.taxonomy

class EditProjectDialog(QDialog):
    def __init__(self, parent=None, project_path=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Project")
        self.setMinimumWidth(400)
        self.project_path = project_path

        with open(self.project_path, "r") as f:
            self.project_data = json.load(f)

        self.name = self.project_data["projectName"]
        self.freq_input = QLineEdit(str(self.project_data["gpsFrequency"]))
        self.taxonomy = self.project_data.get("taxonomy", [])

        self.tax_class_input = QLineEdit()
        self.tax_class_input.setPlaceholderText("Enter Name of Class")
        self.tax_attr_input = QLineEdit()
        self.tax_attr_input.setPlaceholderText("Comma-separated attributes")

        self.tax_list = QListWidget()
        self.refresh_taxonomy_view()

        add_class_btn = QPushButton("Add Class")
        add_class_btn.clicked.connect(self.add_taxonomy_class)

        remove_btn = QPushButton("Remove Selected")
        remove_btn.clicked.connect(self.remove_selected_class)

        layout = QVBoxLayout()
        layout.addWidget(QLabel(f"Editing Project: {self.name}"))
        layout.addWidget(QLabel("GPS Frequency (seconds):"))
        layout.addWidget(self.freq_input)

        tax_layout = QVBoxLayout()
        tax_form = QHBoxLayout()
        tax_form.addWidget(self.tax_class_input)
        tax_form.addWidget(self.tax_attr_input)
        tax_layout.addLayout(tax_form)
        tax_layout.addWidget(add_class_btn)
        tax_layout.addWidget(remove_btn)
        tax_layout.addWidget(QLabel("Taxonomy:"))
        tax_layout.addWidget(self.tax_list)

        button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.save_changes)
        button_box.rejected.connect(self.reject)

        layout.addSpacing(10)
        layout.addLayout(tax_layout)
        layout.addWidget(button_box)

        self.setLayout(layout)
        
        self.tax_list.itemDoubleClicked.connect(self.edit_taxonomy_class)

    def edit_taxonomy_class(self, item):
        index = self.tax_list.row(item)
        class_data = self.taxonomy[index]

        name, ok = QInputDialog.getText(self, "Edit Class Name", "Class Name:", text=class_data["className"])
        if not ok or not name.strip():
            return

        attrs, ok = QInputDialog.getText(
            self, "Edit Attributes", "Comma-separated Attributes:",
            text=", ".join(class_data["attributes"])
        )
        if not ok or not attrs.strip():
            return

        self.taxonomy[index] = {
            "className": name.strip(),
            "attributes": [a.strip() for a in attrs.split(",") if a.strip()]
        }
        self.refresh_tax_list()
        
    def refresh_tax_list(self):
        self.tax_list.clear()
        for t in self.taxonomy:
            self.tax_list.addItem(f"{t['className']}: {', '.join(t['attributes'])}")
    
    def refresh_taxonomy_view(self):
        self.tax_list.clear()
        for entry in self.taxonomy:
            line = f"{entry['className']}: {', '.join(entry['attributes'])}"
            self.tax_list.addItem(line)

    def add_taxonomy_class(self):
        class_name = self.tax_class_input.text().strip()
        attrs = [a.strip() for a in self.tax_attr_input.text().split(",") if a.strip()]
        if class_name and attrs:
            self.taxonomy.append({
                "className": class_name,
                "attributes": attrs
            })
            self.refresh_taxonomy_view()
            self.tax_class_input.clear()
            self.tax_attr_input.clear()

    def remove_selected_class(self):
        selected = self.tax_list.currentRow()
        if selected >= 0:
            del self.taxonomy[selected]
            self.refresh_taxonomy_view()

    def save_changes(self):
        try:
            freq_text = self.freq_input.text().strip()
            if not freq_text.isdigit():
                QMessageBox.warning(self, "Invalid Frequency", "GPS frequency must be a number.")
                return
            freq = int(freq_text)
            if not (5 <= freq <= 20):
                QMessageBox.warning(self, "Invalid Frequency", "GPS frequency must be between 5 and 20 seconds.")
                return
            if not self.taxonomy:
                QMessageBox.warning(self, "Invalid Taxonomy", "You must add at least one taxonomy class.")
                return
            for entry in self.taxonomy:
                if not entry["className"].strip():
                    QMessageBox.warning(self, "Invalid Class", "Each taxonomy class must have a valid name.")
                    return
                if not entry["attributes"]:
                    QMessageBox.warning(self, "Missing Attributes", f"Class '{entry['className']}' must have at least one attribute.")
                    return
            
            self.project_data["gpsFrequency"] = freq
            self.project_data["taxonomy"] = self.taxonomy

            with open(self.project_path, "w") as f:
                json.dump(self.project_data, f, indent=2)

            QMessageBox.information(self, "Saved", "Project updated successfully.")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save changes: {e}")
    
class RouteLoggerDialog(QDialog):
    def __init__(self, parent, project_data, project_path):
        super().__init__(parent)
        self.setWindowTitle(f"Route Logger – {project_data['projectName']}")

        self.freq = project_data["gpsFrequency"] * 1000  # ms for QTimer
        self.taxonomy = project_data["taxonomy"]
        self.meta_stack = []
        self.current_lat, self.current_lon = None, None

        ts = int(time.time())
        route_dir = os.path.join("app_data", "routes")
        os.makedirs(route_dir, exist_ok=True)
        self.current_route_file = os.path.join(
            route_dir,
            f"route_{project_data['projectName']}_{ts}.jsonl"
        )
        open(self.current_route_file, "a").close()  # create file if not exists

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.do_tick)
        
        self.is_logging = False

        self.start_btn = QPushButton("Start Logging")
        self.stop_btn = QPushButton("Stop Logging")
        self.stop_btn.setEnabled(False)

        self.log_view = QListWidget()
        self.meta_form = {}
        self.selected_attrs = {}

        self.meta_buttons = []
        self.meta_layout = QVBoxLayout()
        for entry in self.taxonomy:
            class_name = entry["className"]
            btn = QPushButton(class_name)
            label = QLabel("No attribute selected")
            btn.clicked.connect(lambda _, e=entry, l=label: self.open_meta_selector(e, l))

            self.meta_form[class_name] = label
            self.selected_attrs[class_name] = None

            row = QHBoxLayout()
            row.addWidget(btn)
            row.addWidget(label)
            self.meta_layout.addLayout(row)

        self.submit_meta_btn = QPushButton("Submit Meta")
        self.submit_meta_btn.setEnabled(False)
        self.submit_meta_btn.clicked.connect(self.submit_meta)
        self.meta_layout.addWidget(self.submit_meta_btn)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.start_btn)
        btn_layout.addWidget(self.stop_btn)

        main_layout = QVBoxLayout()
        main_layout.addLayout(btn_layout)
        main_layout.addLayout(self.meta_layout)
        main_layout.addWidget(QLabel("Logged Entries:"))
        main_layout.addWidget(self.log_view)
        self.setLayout(main_layout)

        self.start_btn.clicked.connect(self.start_logging)
        self.stop_btn.clicked.connect(self.stop_logging)
        
    def update_submit_button_state(self):
        if not self.is_logging:
            self.submit_meta_btn.setEnabled(False)
            return

        any_selected = any(attr is not None for attr in self.selected_attrs.values())
        self.submit_meta_btn.setEnabled(any_selected)

    def open_meta_selector(self, entry, label_widget):
        attrs, ok = QInputDialog.getItem(
            self, f"Select {entry['className']}",
            "Attribute:", entry["attributes"], 0, False
        )
        if ok:
            label_widget.setText(attrs)
            self.selected_attrs[entry["className"]] = attrs
            self.update_submit_button_state()

    def submit_meta(self):
        submitted_at = int(time.time())
        meta_data = {
            cls: attr
            for cls, attr in self.selected_attrs.items()
            if attr is not None
        }

        if meta_data:
            self.meta_stack.append({
                "submitted_at": submitted_at,
                "meta_data": meta_data
            })

        # Clear selections
        for class_name, label in self.meta_form.items():
            label.setText("No attribute selected")
            self.selected_attrs[class_name] = None

        self.update_submit_button_state()

        QMessageBox.information(self, "Meta Submitted", "Your meta data has been recorded.")

    def start_logging(self):
        open(self.current_route_file, "a").close()
        self.is_logging = True
        self.timer.start(self.freq)
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.update_submit_button_state()

    def update_location(self, lat, lon):
        self.current_lat = lat
        self.current_lon = lon

    def stop_logging(self):
        self.is_logging = False
        self.timer.stop()
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.update_submit_button_state()
        QMessageBox.information(self, "Logging stopped",
                                f"Logs saved to {self.current_route_file}")

    def do_tick(self):
        lat, lon = self.get_current_location()
        tick_ts = int(time.time())

        if self.meta_stack:
            meta = self.meta_stack.pop(0)
            log = {
                "tick_timestamp": tick_ts,
                "meta_submitted_at": meta["submitted_at"],
                "latitude": lat,
                "longitude": lon,
                "meta_data": meta["meta_data"]
            }
        else:
            log = {
                "tick_timestamp": tick_ts,
                "latitude": lat,
                "longitude": lon,
                "meta_data": {}
            }

        with open(self.current_route_file, "a") as f:
            f.write(json.dumps(log) + "\n")

        self.log_view.addItem(f"{log['tick_timestamp']}: {log['meta_data']}")

    def get_current_location(self):
        # Simulated coordinates around a central point (Delhi)
        return 28.6448 + random() * 0.001, 77.2167 + random() * 0.001
