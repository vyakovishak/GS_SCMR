# ---- Start for AdminLoginDialog.py ---- #
import json
from PySide6.QtWidgets import QTableWidget, QPushButton, QTableWidgetItem, QHeaderView, QInputDialog, QMessageBox, \
    QHBoxLayout, QLineEdit, QVBoxLayout, QLabel, QDialog
from Utilities.utils import load_agents

class AdminLoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Admin Login")
        self.setContentsMargins(5, 5, 5, 5)

        layout = QVBoxLayout(self)

        username_layout = QHBoxLayout()
        self.username_label = QLabel("Username:")
        self.username_input = QLineEdit()
        username_layout.addWidget(self.username_label)
        username_layout.addWidget(self.username_input)
        layout.addLayout(username_layout)

        password_layout = QHBoxLayout()
        self.password_label = QLabel("Password:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        password_layout.addWidget(self.password_label)
        password_layout.addWidget(self.password_input)
        layout.addLayout(password_layout)

        button_layout = QHBoxLayout()
        self.login_button = QPushButton("Login")
        self.login_button.clicked.connect(self.verify_credentials)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.login_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)

    def verify_credentials(self):
        # Replace 'admin' and 'password' with the correct admin credentials
        if self.username_input.text() == "admin" and self.password_input.text() == "password":
            self.accept()
        else:
            QMessageBox.warning(self, "Warning", "Invalid username or password.")


class EditAgentDialog(QDialog):
    def __init__(self, agent_name, agent_data):
        super().__init__()

        self.setWindowTitle(f"Edit {agent_name}")
        self.agent_name = agent_name
        self.agent_data = agent_data

        layout = QVBoxLayout(self)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText(agent_name)
        layout.addWidget(QLabel("Agent Name:"))
        layout.addWidget(self.name_input)

        self.weekly_input = QLineEdit()
        self.weekly_input.setPlaceholderText(str(agent_data['Weekly']))
        layout.addWidget(QLabel("Agent Weekly Hours:"))
        layout.addWidget(self.weekly_input)

        self.monthly_input = QLineEdit()
        self.monthly_input.setPlaceholderText(str(agent_data['Monthly']))
        layout.addWidget(QLabel("Agent Monthly Hours:"))
        layout.addWidget(self.monthly_input)

        self.apply_button = QPushButton("Apply")
        self.apply_button.clicked.connect(self.apply_changes)
        layout.addWidget(self.apply_button)

        self.delete_button = QPushButton("Delete")
        self.delete_button.clicked.connect(self.delete_agent)
        layout.addWidget(self.delete_button)

    def apply_changes(self):
        updated_name = self.name_input.text() if self.name_input.text() else self.agent_name
        updated_weekly = int(self.weekly_input.text()) if self.weekly_input.text() else self.agent_data['Weekly']
        updated_monthly = int(self.monthly_input.text()) if self.monthly_input.text() else self.agent_data['Monthly']

        self.agent_name = updated_name
        self.agent_data['Weekly'] = updated_weekly
        self.agent_data['Monthly'] = updated_monthly
        self.done(2)  # Return 2 if changes should be applied

    def delete_agent(self):
        # Show a warning message before deleting the agent
        warning_msg = QMessageBox()
        warning_msg.setIcon(QMessageBox.Warning)
        warning_msg.setWindowTitle("Delete Agent")
        warning_msg.setText("Are you sure you want to delete this agent?")
        warning_msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)

        result = warning_msg.exec()

        if QMessageBox.Yes == result:
            self.done(1)  # Return 1 if the agent should be deleted

        elif QMessageBox.No == result:
            return


class AdminManagement(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Admin Management")
        self.agents = load_agents(agent_names_only=False)
        print(self.agents)
        self.resize(600, 400)
        self.setContentsMargins(5, 5, 5, 5)

        layout = QVBoxLayout(self)

        tables_layout = QHBoxLayout()

        # ARA table
        self.ara_table_widget = QTableWidget()
        self.populate_table_widget(self.ara_table_widget, "ARA")

        ara_label = QLabel("ARA")
        ara_layout = QVBoxLayout()
        ara_layout.addWidget(ara_label)
        ara_layout.addWidget(self.ara_table_widget)
        tables_layout.addLayout(ara_layout)

        # CA table
        self.ca_table_widget = QTableWidget()
        self.populate_table_widget(self.ca_table_widget, "CA")

        ca_label = QLabel("CA")
        ca_layout = QVBoxLayout()
        ca_layout.addWidget(ca_label)
        ca_layout.addWidget(self.ca_table_widget)
        tables_layout.addLayout(ca_layout)

        layout.addLayout(tables_layout)

        add_agent_layout = QHBoxLayout()

        self.agent_name_input = QLineEdit()
        self.agent_name_input.setPlaceholderText("Enter Agent Name")
        add_agent_layout.addWidget(self.agent_name_input)

        self.add_agent_button = QPushButton("Add Agent")
        self.add_agent_button.clicked.connect(self.add_agent)
        add_agent_layout.addWidget(self.add_agent_button)

        layout.addLayout(add_agent_layout)

    def create_table_widget(self, group):
        table_widget = QTableWidget()
        table_widget.setColumnCount(2)
        table_widget.setHorizontalHeaderLabels(["Agent", "Edit"])
        table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.populate_table_widget(table_widget, group)

        return table_widget

    def populate_table_widget(self, table_widget, group):
        print(self.agents)
        print(group)
        agents = self.agents["Agents"][group]
        table_widget.setRowCount(len(agents))
        table_widget.setColumnCount(2)
        table_widget.setHorizontalHeaderLabels(["Agent", "Edit"])
        table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table_widget.setEditTriggers(QTableWidget.NoEditTriggers)

        for row, (agent_name, agent_data) in enumerate(agents.items()):
            table_widget.setItem(row, 0, QTableWidgetItem(agent_name))

            edit_button = QPushButton("Edit")
            edit_button.clicked.connect(lambda *_, r=row, g=group: self.edit_agent(r, g))
            table_widget.setCellWidget(row, 1, edit_button)

    def add_agent(self):
        new_agent_name = self.agent_name_input.text()

        if not new_agent_name:
            QMessageBox.warning(self, "Error", "Please enter a valid agent name.")
            return

        if not self.is_agent_name_unique(new_agent_name):
            QMessageBox.warning(self, "Error", "This agent name already exists. Please enter a unique agent name.")
            return

        if not new_agent_name:
            QMessageBox.warning(self, "Warning", "Please enter a new agent name.")
            return

        group, _ = QInputDialog.getItem(self, "Select Group", "Select group for the new agent:", ["ARA", "CA"],
                                        editable=False)
        if not group:
            return

        weekly_hours, ok = QInputDialog.getInt(self, "Weekly Hours", "Enter the weekly hours for the new agent:")
        if not ok:
            return

        monthly_hours, ok = QInputDialog.getInt(self, "Monthly Hours", "Enter the monthly hours for the new agent:")
        if not ok:
            return

        self.agents["Agents"][group][new_agent_name] = {"Weekly": weekly_hours, "Monthly": monthly_hours}
        self.update_agents()

        table_widget = self.ara_table_widget if group == "ARA" else self.ca_table_widget
        row = table_widget.rowCount()
        table_widget.setRowCount(row + 1)

        agent_item = QTableWidgetItem(new_agent_name)
        table_widget.setItem(row, 0, agent_item)

        edit_button = QPushButton("Edit")
        edit_button.clicked.connect(lambda *_, r=row, g=group: self.edit_agent(r, g))
        table_widget.setCellWidget(row, 1, edit_button)

        self.agent_name_input.clear()

    def create_widget_table(self, group):
        agents = self.agents["Agents"][group]

        table_widget = QTableWidget()
        table_widget.setRowCount(len(agents))
        table_widget.setColumnCount(2)
        table_widget.setHorizontalHeaderLabels(["Agent", "Edit"])
        table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        for row, agent in enumerate(agents):
            agent_item = QTableWidgetItem(agent)
            table_widget.setItem(row, 0, agent_item)

            edit_button = QPushButton("Edit")
            edit_button.clicked.connect(lambda *_, r=row, g=group: self.edit_agent(r, g))
            table_widget.setCellWidget(row, 1, edit_button)

        table_widget.setEditTriggers(QTableWidget.NoEditTriggers)

        return table_widget

    def find_agent_in_settings(self, agent_name):
        print(self.agents)
        for group, agents in self.agents["Agents"].items():
            if agent_name in agents:
                return group, agents[agent_name]
        return None, None

    def edit_agent(self, row, group):
        table_widget = self.ara_table_widget if group == "ARA" else self.ca_table_widget
        agent_name = table_widget.item(row, 0).text()
        agent_data = self.agents["Agents"][group][agent_name]

        edit_dialog = EditAgentDialog(agent_name, agent_data)
        result = edit_dialog.exec()

        if result == 1:
            # Delete the agent from the settings
            del self.agents["Agents"][group][agent_name]
            self.update_agents()

            # Remove the agent from the list and the table
            table_widget.removeRow(row)

            # Update edit button connections for the remaining rows
            for r in range(row, table_widget.rowCount()):
                edit_button = table_widget.cellWidget(r, 1)
                edit_button.clicked.disconnect()
                edit_button.clicked.connect(lambda *_, r=r, g=group: self.edit_agent(r, g))

        elif result == 2:
            # Apply changes
            old_agent_name = agent_name
            new_agent_name = edit_dialog.agent_name
            if old_agent_name != new_agent_name:
                self.agents["Agents"][group][new_agent_name] = self.agents["Agents"][group].pop(old_agent_name)
                table_widget.item(row, 0).setText(new_agent_name)

            self.agents["Agents"][group][new_agent_name]['Weekly'] = edit_dialog.agent_data['Weekly']
            self.agents["Agents"][group][new_agent_name]['Monthly'] = edit_dialog.agent_data['Monthly']
            self.update_agents()

    def is_agent_name_unique(self, agent_name):
        for group in self.agents["Agents"].values():
            if agent_name in group:
                return False
        return True

    def update_agents(self):
        with open("./Dependents/GS_Files/Agents.json", "w") as f:
            json.dump(self.agents, f, indent=2)

# ---- End for AdminLoginDialog.py ---- #