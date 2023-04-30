# ---- Start for StatsDialog.py ---- #
from collections import defaultdict
from datetime import timedelta, datetime, date
import numpy as np
import pandas as pd
from PySide6.QtCharts import QLineSeries, QValueAxis, QDateTimeAxis, QChart, QBarCategoryAxis, QBarSet, QBarSeries, \
    QChartView
from PySide6.QtCore import QDateTime
from PySide6.QtGui import QFont, Qt, QPainter
from PySide6.QtWidgets import QMessageBox, QDialogButtonBox, QLabel, QComboBox, QCalendarWidget, QVBoxLayout, QDialog, \
    QPushButton, QGroupBox, QHBoxLayout

from Utilities.utils import load_agents


class StatsDialog(QDialog):
    def __init__(self, db, parent=None):
        super().__init__()
        self.db = db
        self.setWindowTitle("Stats")
        self.resize(800, 600)
        self.closed_units_data = {}
        self.check_out_data = {}

        # Set default start and end dates
        self.end_date = date.today()
        self.start_date = self.end_date - timedelta(days=30)
        self.selected_agent = "ALL"

        main_layout = QVBoxLayout()
        layout = QHBoxLayout()

        self.date_range_label = QLabel()
        main_layout.addWidget(self.date_range_label)

        self.graph_group_box = QGroupBox("Closed By")
        graph_layout = QVBoxLayout()

        # Use your database function to get the data
        self.get_closed_units_data()
        self.chart = self.generate_chart(self.closed_units_data, "Closed Units", "Date", "Closed Units")

        self.chart_view = QChartView(self.chart)
        self.chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)

        graph_layout.addWidget(self.chart_view)
        self.graph_group_box.setLayout(graph_layout)

        # Check Out group box
        self.check_out_group_box = QGroupBox("Check Out By")
        check_out_layout = QVBoxLayout()

        self.check_out_chart = self.generate_chart(self.check_out_data, "Check Out Units", "Date", "Check Out Units")

        check_out_chart_view = QChartView(self.check_out_chart)
        check_out_chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)

        check_out_layout.addWidget(check_out_chart_view)
        self.check_out_group_box.setLayout(check_out_layout)

        layout.addWidget(self.graph_group_box)
        layout.addWidget(self.check_out_group_box)

        self.utilization_group_box = QGroupBox("Utilization")
        utilization_layout = QVBoxLayout()
        self.utilization_data = self.get_utilization_data()

        # self.utilization_data = self.get_dummy_data()

        print(f"Utilization Data: {self.utilization_data}")

        self.utilization_chart = self.generate_chart(self.utilization_data, "Utilization", "Date", "Utilization",
                                                     chart_type="line")

        self.utilization_chart_view = QChartView(self.utilization_chart)
        self.utilization_chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        utilization_layout.addWidget(self.utilization_chart_view)
        self.utilization_group_box.setLayout(utilization_layout)
        layout.addWidget(self.utilization_group_box)  # This line is moved outside the if statement

        main_layout.addLayout(layout)

        self.closed_units_filter_btn = QPushButton("Filters")
        self.closed_units_filter_btn.clicked.connect(lambda: self.show_filters_dialog("closed_units"))
        graph_layout.addWidget(self.closed_units_filter_btn)

        self.checkout_units_filter_btn = QPushButton("Filters")
        self.checkout_units_filter_btn.clicked.connect(lambda: self.show_filters_dialog("check_out_units"))
        check_out_layout.addWidget(self.checkout_units_filter_btn)

        self.setLayout(main_layout)

    def get_utilization_data(self):
        adjusted_end_date = self.end_date + timedelta(days=1)
        raw_data = self.db.select_closed_orders_by_agent(self.start_date, adjusted_end_date, self.selected_agent)
        agent_weekly_hours = dict(load_agents(hours_type="weekly", agent_names_only=False))
        utilization_data = {}

        if raw_data:
            # Sort raw_data by date
            raw_data.sort(key=lambda x: x[0])

            # Process sorted raw_data to accumulate utilization per agent
            accumulated_data = []
            accumulated_minutes_per_agent = defaultdict(int)
            for row in raw_data:
                completion_date_str = row[0].split(' ')[0]  # Extract only the date part
                completion_date = datetime.datetime.strptime(completion_date_str, '%Y-%m-%d').date()
                agent_name = row[1]
                bop_time_minutes = row[2]

                accumulated_minutes_per_agent[agent_name] += bop_time_minutes
                accumulated_data.append((completion_date, agent_name, accumulated_minutes_per_agent[agent_name]))

            print("Accumulated data:", accumulated_data)

            # Calculate utilization percentage
            utilization_percentage_data = defaultdict(dict)
            for date, agent_name, accumulated_time in accumulated_data:
                weekly_hours = agent_weekly_hours.get(agent_name, 0)
                days_diff = (date - self.start_date).days + 1
                total_hours = (weekly_hours / 7) * days_diff
                if total_hours > 0:
                    bop_time_hours = accumulated_time / 60
                    utilization_percentage = (bop_time_hours / total_hours) * 100
                    utilization_percentage = round(utilization_percentage,
                                                   2)  # Round the percentage to 2 decimal places
                    utilization_percentage_data[agent_name][date] = utilization_percentage

            print("Utilization percentage data:", dict(utilization_percentage_data))
            # Convert datetime objects back to string format for compatibility with the generate_chart function
            utilization_percentage_data = {
                agent: {date.strftime('%Y-%m-%d'): value for date, value in date_values.items()} for
                agent, date_values in
                utilization_percentage_data.items()}
        return utilization_percentage_data

    def get_closed_units_data(self):
        adjusted_end_date = self.end_date + timedelta(days=1)
        raw_data = self.db.select_closed_orders_by_agent(self.start_date, adjusted_end_date, self.selected_agent)

        if raw_data:
            data_dict = {}
            for row in raw_data:
                completion_date = row[0].split(' ')[0]  # Extract only the date part
                agent_name = row[1]

                if agent_name not in data_dict:
                    data_dict[agent_name] = {}

                if completion_date not in data_dict[agent_name]:
                    data_dict[agent_name][completion_date] = 1
                else:
                    data_dict[agent_name][completion_date] += 1

            self.closed_units_data = data_dict

        self.get_checkout_units_data()

    def get_checkout_units_data(self):
        adjusted_end_date = self.end_date + timedelta(days=1)
        raw_data_check_out = self.db.select_checkout_orders_by_agent(self.start_date, adjusted_end_date,
                                                                     self.selected_agent)
        if raw_data_check_out:
            data_dict_check_out = {}
            for row in raw_data_check_out:
                completion_date = row[0].split(' ')[0]  # Extract only the date part
                agent_name = row[1]

                if agent_name not in data_dict_check_out:
                    data_dict_check_out[agent_name] = {}

                if completion_date not in data_dict_check_out[agent_name]:
                    data_dict_check_out[agent_name][completion_date] = 1
                else:
                    data_dict_check_out[agent_name][completion_date] += 1
            self.check_out_data = data_dict_check_out

    @staticmethod
    def generate_bar_chart(data, title, x_name, y_name):
        chart = QChart()
        chart.setTitle(title)

        axis_x = QDateTimeAxis()
        axis_x.setFormat("MMM dd")
        axis_x.setTitleText(x_name)

        axis_y = QValueAxis()
        axis_y.setTitleText(y_name)
        axis_y.setTickCount(11)

        series = QBarSeries()

        for index, row in data.iterrows():
            bar_set = QBarSet(index)
            for date, value in row.items():
                bar_set.append(value)

            series.append(bar_set)

        chart.addSeries(series)
        chart.setAxisX(axis_x, series)
        chart.setAxisY(axis_y, series)

        # Setting the categories for the x-axis labels
        categories = [QDateTime.fromString(date_str, "yyyy-MM-dd").toString("yyyy-MM-dd") for date_str in data.columns]
        bar_categories = QBarCategoryAxis()
        bar_categories.append(categories)
        chart.setAxisX(bar_categories, series)

        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignBottom)

        return chart


    @staticmethod
    def generate_line_chart(data, title, x_name, y_name):
        chart = QChart()
        chart.setTitle(title)

        axis_x = QDateTimeAxis()
        axis_x.setFormat("MMM dd")
        axis_x.setTitleText(x_name)

        axis_y = QValueAxis()
        axis_y.setRange(0, 100)  # Adjust the range values as needed
        axis_y.setTitleText(y_name)
        axis_y.setTickCount(11)

        for index, row in data.iterrows():
            line_series = QLineSeries()
            line_series.setName(index)
            data_points = 0

            # Sort dates
            sorted_dates = sorted(row.items(), key=lambda x: x[0])

            for date, value in sorted_dates:
                if value > 0:  # Only append points with non-zero values
                    qt_date = QDateTime.fromString(date, "yyyy-MM-dd")
                    print(f"Appending point: {qt_date}, {value}")  # Debugging line
                    line_series.append(np.int64(qt_date.toMSecsSinceEpoch()), value)

                    data_points += 1

            # Duplicate the single data point if there's only one
            if data_points == 1:
                last_point = line_series.at(0)
                new_date = QDateTime.fromMSecsSinceEpoch(
                    int(last_point.x()) + 86400000)  # Add one day (in milliseconds)
                line_series.append(np.int64(new_date.toMSecsSinceEpoch()), last_point.y())

            chart.addSeries(line_series)
            chart.setAxisX(axis_x, line_series)
            chart.setAxisY(axis_y, line_series)

        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignBottom)

        return chart

    @staticmethod
    def calculate_cumulative_utilization_data(raw_data):
        cumulative_data = {}

        for agent, date_values in raw_data.items():
            cumulative_data[agent] = {}
            cumulative_sum = 0

            for date, value in date_values.items():
                cumulative_sum += value
                cumulative_data[agent][date] = cumulative_sum

        return cumulative_data

    @staticmethod
    def generate_chart(data, title, x_name, y_name, chart_type="bar"):
        if not data:
            return None
        df = pd.DataFrame.from_dict(data, orient='index').fillna(0)
        if chart_type == "bar":
            return StatsDialog.generate_bar_chart(df, title, x_name, y_name)
        elif chart_type == "line":
            return StatsDialog.generate_line_chart(df, title, x_name, y_name)

    def show_filters_dialog(self, graph_type):
        filters_dialog = FiltersDialog()
        if filters_dialog.exec() == QDialog.DialogCode.Accepted:
            self.start_date, self.end_date, self.selected_agent = filters_dialog.get_filters()
            self.update_date_range_label(graph_type)

    def update_date_range_label(self, graph_type):
        start_date_str = self.start_date.toString("yyyy-MM-dd")
        end_date_str = self.end_date.toString("yyyy-MM-dd")
        if graph_type == "closed_units":
            self.graph_group_box.setTitle(
                f"Closed Units | Date range: {start_date_str} - {end_date_str} | Agent: {self.selected_agent}")
        elif graph_type == "check_out_units":
            self.check_out_group_box.setTitle(
                f"Check Out Units | Date range: {start_date_str} - {end_date_str} | Agent: {self.selected_agent}")


class FiltersDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Filters")
        self.resize(700, 400)

        layout = QVBoxLayout()

        # Add calendar widgets and labels for start and end dates
        self.calendar = QCalendarWidget()
        layout.addWidget(self.calendar)

        self.range_label = QLabel()
        font = QFont()
        font.setPointSize(14)
        font.setBold(True)
        self.range_label.setFont(font)
        self.range_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.range_label)

        self.start_date = None
        self.end_date = None

        self.calendar.clicked.connect(self.update_date_range)

        # Add buttons for applying filters and closing the dialog
        button_box = QDialogButtonBox(QDialogButtonBox.Cancel | QDialogButtonBox.Apply)
        button_box.button(QDialogButtonBox.Apply).clicked.connect(self.apply_filters)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        # Add QLabel and QComboBox for agents
        self.agent_label = QLabel("Agent")
        self.agent_label.setStyleSheet("font-size: 14px;")
        layout.addWidget(self.agent_label)

        self.agent_combobox = QComboBox()
        self.agent_combobox.addItem("ALL")
        self.agent_combobox.addItems(load_agents(agent_names_only=True))
        layout.addWidget(self.agent_combobox)

        self.setLayout(layout)

    def update_date_range(self, clicked_date):
        if not self.start_date:
            self.start_date = clicked_date
            self.end_date = None
        elif not self.end_date:
            if clicked_date < self.start_date:
                self.start_date, self.end_date = clicked_date, self.start_date
            else:
                self.end_date = clicked_date
        else:
            self.start_date = clicked_date
            self.end_date = None

        # Update label with selected date range
        if self.start_date and not self.end_date:
            self.range_label.setText(self.start_date.toString("yyyy-MM-dd"))
        elif self.start_date and self.end_date:
            self.range_label.setText(
                f"{self.start_date.toString('yyyy-MM-dd')} - {self.end_date.toString('yyyy-MM-dd')}")

    def apply_filters(self):
        if self.start_date is None and self.end_date is None:
            QMessageBox.warning(self, "Warning", "Please select a date range.")
            return
        else:
            self.accept()

    def get_filters(self):
        return self.start_date, self.end_date, self.agent_combobox.currentText()

# ---- End for StatsDialog.py ---- #