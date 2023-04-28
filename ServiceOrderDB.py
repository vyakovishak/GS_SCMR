# ServiceOrderDB.py

import datetime
import json
import sqlite3
import os


class ServiceOrderDB:
    def __init__(self, path_to_db="ServiceOrders.db", status_bar=None):
        """
            Constructor for the ServiceOrderDB class.
            :param path_to_db: Path to the SQLite database file.
            :param status_bar: A reference to a QStatusBar widget for displaying status messages.
        """
        self.path_to_db = path_to_db
        self.status_bar = status_bar

    @property
    def connection(self):
        """
            Property that returns a connection to the SQLite database.
        """
        return sqlite3.connect(self.path_to_db)

    def execute(self, sql: str, parameters: tuple = None, fetchone=False, fetchall=False, commit=False):
        if not parameters:
            parameters = tuple()
        connection = self.connection
        cursor = connection.cursor()
        #connection.set_trace_callback(logger)
        cursor.execute(sql, parameters)

        data = None
        if commit:
            connection.commit()
        if fetchone:
            data = cursor.fetchone()
        if fetchall:
            data = cursor.fetchall()
        connection.close()

        return data

    def create_table_users(self):
        """
            Creates the "ServiceOrders" table in the SQLite database if it does not already exist.
        """
        sql = """
                CREATE TABLE IF NOT EXISTS ServiceOrders (
                ServiceOrder VARCHAR(255) PRIMARY KEY,
                Location VARCHAR(255),
                CompletionDate DATETIME,
                ClosedBy VARCHAR(255),
                Status VARCHAR(255),
                Comments TEXT,
                LastUpdated DATETIME,
                UpdatedBy VARCHAR(255),
                CheckOutBy VARCHAR(255),
                CheckOutDate DATETIME,
                CheckedOut VARCHAR(255) DEFAULT 'NO',
                CFI VARCHAR(255) DEFAULT 'NO',
                Scanned BOOLEAN DEFAULT FALSE,
                ResCode  VARCHAR(255) DEFAULT 'None',
                BOPTime  VINT DEFAULT '0',
                FOPTime  INT DEFAULT '0',
                TotalTime  INT DEFAULT '0',
                PaymentStatus VARCHAR(255) DEFAULT 'NO'
            );"""

        self.execute(sql, commit=True)

    def add_service_order(self,
                          ServiceOrder: int,
                          Location: str,
                          CompletionDate: str,
                          ClosedBy: str,
                          Status: str,
                          Comments: str,
                          Payment: str
                          ):

        after = {
            "ServiceOrder": ServiceOrder,
            "Location": Location,
            "CompletionDate": CompletionDate,
            "ClosedBy": ClosedBy,
            "Status": Status,
            "Comments": Comments,
            "PaymentStatus":Payment
        }

        self.log_update("Add Service Order", operator=ClosedBy, ServiceOrder=ServiceOrder, before={}, after=after)

        LastUpdated = ''
        UpdatedBy = ''
        CheckOutBy = ''
        CheckOutDate = ''
        sql_command = "INSERT OR IGNORE INTO ServiceOrders(ServiceOrder, Location, CompletionDate, ClosedBy, Status, " \
                      "Comments, LastUpdated, UpdatedBy, CheckOutBy, CheckOutDate, PaymentStatus) VALUES(?,?,?,?,?,?,?,?,?,?,?)"

        parameters = (ServiceOrder,
                      Location,
                      CompletionDate,
                      ClosedBy,
                      Status,
                      Comments,
                      LastUpdated,
                      UpdatedBy,
                      CheckOutBy,
                      CheckOutDate,
                      Payment
                      )

        self.execute(sql_command, parameters=parameters, commit=True)

    def select_closed_orders_by_agent(self, start_date, end_date, agent=None):
        if agent is not None and agent != "ALL":
            agent_command = f'AND ClosedBy="{agent}"'
        else:
            agent_command = ""
        sql = f"""SELECT CompletionDate, ClosedBy, BOPTime as closed_units
                  FROM ServiceOrders
                  WHERE CompletionDate BETWEEN ? AND ? {agent_command} AND CFI= "NO" """

        return self.execute(sql, parameters=(start_date, end_date), fetchall=True)

    def select_checkout_orders_by_agent(self, start_date, end_date, agent=None):
        if agent is not None and agent != "ALL":
            agent_command = f'AND ClosedBy="{agent}"'
        else:
            agent_command = ""
        sql = f"""SELECT CompletionDate, CheckOutBy as closed_units
                  FROM ServiceOrders
                  WHERE CompletionDate BETWEEN ? AND ? {agent_command} AND CheckedOut="YES" AND CFI="NO" """

        return self.execute(sql, parameters=(start_date, end_date), fetchall=True)

    # Selects all service orders that are not checked out
    def select_service_order(self, so):
        sql_command = "SELECT * FROM ServiceOrders WHERE ServiceOrder=?"
        return self.execute(sql_command, parameters=(so,), fetchall=True)

    def select_all_unchecked_out(self):
        sql_command = "SELECT * FROM ServiceOrders WHERE CheckedOut='NO' AND CFI='NO'"
        return self.execute(sql_command, fetchall=True)

    def select_all_scanned_out(self):
        sql_command = "SELECT * FROM ServiceOrders WHERE CheckedOut='NO' AND Scanned=0 AND CFI='NO'"
        return self.execute(sql_command, fetchall=True)

    # Updates the check-out operator for a given service order
    def update_checkout_info(self, status, timestamp, operator, so):
        current_data = self.select_unit(column='CheckedOut, CheckoutDate, CheckOutBy', ServiceOrder=so)  # [(0, '', '')]

        current_data_tuple = current_data[0]
        before_data = {"CheckedOut": current_data_tuple[0], "CheckoutDate": current_data_tuple[1],
                       "CheckOutBy": current_data_tuple[2]}
        after_data = {"CheckedOut": status, "CheckoutDate": timestamp, "CheckOutBy": operator}
        self.log_update("Checkout", ServiceOrder=so, operator=operator, before=before_data, after=after_data)

        sql_command = "UPDATE ServiceOrders SET CheckedOut = ?, CheckoutDate = ?, CheckOutBy = ? WHERE ServiceOrder=?"
        return self.execute(sql_command, parameters=(status, timestamp, operator, so), commit=True)

    def update_last_updated(self, last_updated, so, operator):
        current_last_updated = self.select_unit(column='LastUpdated', ServiceOrder=so)
        self.log_update("Updated Check Out By", ServiceOrder=so, operator=operator,
                        before={"LastUpdated": current_last_updated},
                        after={"LastUpdated": last_updated})
        sql_command = "UPDATE ServiceOrders SET LastUpdated=? WHERE ServiceOrder=?"
        return self.execute(sql_command, parameters=(last_updated, so), commit=True)

    def rescan_service_order_update(self, location, updated_by, scanned_status, last_updated, so, operator):
        current_location = self.select_unit(column='Location', ServiceOrder=so)
        current_updated_by = self.select_unit(column='UpdatedBy', ServiceOrder=so)

        self.log_update("Rescan", ServiceOrder=so, operator=operator,
                        before={"Location": current_location[0][0], "UpdatedBy": current_updated_by[0][0]},
                        after={"Location": location, "UpdatedBy": updated_by})

        sql_command = """UPDATE ServiceOrders SET Location=?, UpdatedBy=?, Scanned=?, LastUpdated=? WHERE 
        ServiceOrder=?"""
        return self.execute(sql_command, parameters=(location, updated_by, scanned_status, last_updated, so),
                            commit=True)

    def update_scanned_status(self, scanned_status, so, operator, log=True):
        if log:
            current_scanned_status = self.select_unit(column='Scanned', ServiceOrder=so)
            self.log_update("Updated Scanned", ServiceOrder=so, operator=operator,
                            before={"Scanned": current_scanned_status},
                            after={"Scanned": scanned_status})
        sql_command = "UPDATE ServiceOrders SET Scanned=? WHERE ServiceOrder=?"
        return self.execute(sql_command, parameters=(scanned_status, so), commit=True)

    def update_updated_by(self, updated_by, so, operator):
        current_updated_by = self.select_unit(column='UpdatedBy', ServiceOrder=so)
        self.log_update("Updated Updated By", ServiceOrder=so, operator=operator,
                        before={"UpdatedBy": current_updated_by}, after={"UpdatedBy": updated_by})
        sql_command = "UPDATE ServiceOrders SET UpdatedBy=? WHERE ServiceOrder=?"
        return self.execute(sql_command, parameters=(updated_by, so), commit=True)

    # Updates the check-out date for a given service order
    def update_check_out_date(self, check_out_date, so, operator):
        current_data = self.select_unit(column='CheckOutDate', ServiceOrder=so)
        self.log_update("Updated Check Out Date", ServiceOrder=so, operator=operator, before=current_data,
                        after=check_out_date)
        sql_command = "UPDATE ServiceOrders SET CheckOutDate=? WHERE ServiceOrder=?"
        return self.execute(sql_command, parameters=(check_out_date, so), commit=True)

    # Selects all service orders in the database
    def select_all_service_orders(self):
        sql_command = "SELECT * FROM ServiceOrders"
        return self.execute(sql_command, fetchall=True)

    def select_all_service_orders_not_deleted(self):
        sql_command = "SELECT * FROM ServiceOrders WHERE CFI='NO'"
        return self.execute(sql_command, fetchall=True)

    def check_location_exists(self, location: str) -> bool:

        sql_command = "SELECT * FROM ServiceOrders WHERE Location = ? AND CheckedOut='NO' AND CFI='NO'"
        result = self.execute(sql_command, parameters=(location,), fetchall=True)
        return len(result) > 0

    # Updates a service order with the given parameters
    def update_service_order(self, ServiceOrder: int, operator, before, after, log=True):
        sql_command = f"UPDATE ServiceOrders SET "
        parameters = []
        for key, value in after.items():
            sql_command += f"{key}=?, "

            parameters.append(value)

        sql_command = sql_command.rstrip(", ")
        sql_command += " WHERE ServiceOrder=?"
        parameters.append(ServiceOrder)

        # Logging functionality
        if log:
            operation = "Update Service Order"
            self.log_update(operation, ServiceOrder=ServiceOrder, operator=operator, before=before, after=after)

        return self.execute(sql_command, parameters=tuple(parameters), commit=True)

    def update_location(self, location, so, operator):
        current_location = self.select_unit(column='Location', ServiceOrder=so)
        self.log_update("Updated Location", ServiceOrder=so, operator=operator, before={"Location": current_location},
                        after={"Location": location})
        sql_command = "UPDATE ServiceOrders SET Location=? WHERE ServiceOrder=?"
        return self.execute(sql_command, parameters=(location, so), commit=True)

    def update_completion_date(self, completion_date, so, operator):
        current_data = self.select_unit(column='CompletionDate', ServiceOrder=so)
        self.log_update("Updated Location", ServiceOrder=so, operator=operator, before=current_data,
                        after=completion_date)
        sql_command = "UPDATE ServiceOrders SET DATE(CompletionDate)=? WHERE ServiceOrder=?"
        return self.execute(sql_command, parameters=(completion_date, so), commit=True)

    def update_closed_by(self, closed_by, so, operator):
        current_data = self.select_unit(column='ClosedBy', ServiceOrder=so)
        self.log_update("Updated Location", ServiceOrder=so, operator=operator, before=current_data, after=closed_by)
        sql_command = "UPDATE ServiceOrders SET ClosedBy=? WHERE ServiceOrder=?"
        return self.execute(sql_command, parameters=(closed_by, so), commit=True)

    def update_status(self, status, so, operator):
        current_data = self.select_unit(column='Status', ServiceOrder=so)
        self.log_update("Updated Location",
                        ServiceOrder=so,
                        operator=operator,
                        before=current_data,
                        after=status)
        sql_command = "UPDATE ServiceOrders SET Status=? WHERE ServiceOrder=?"
        return self.execute(sql_command, parameters=(status, so), commit=True)

    def update_res_codes(self, res_code_data, so, operator):
        ResCode = self.select_unit(column='ResCode', ServiceOrder=so)
        BOPTime = self.select_unit(column='BOPTime', ServiceOrder=so)
        FOPTime = self.select_unit(column='FOPTime', ServiceOrder=so)
        TotalTime = self.select_unit(column='TotalTime', ServiceOrder=so)

        before = {
            "ResCodes": {"Code": ResCode,
                         "BOB_time": BOPTime,
                         "FOP_time": FOPTime,
                         "Total_time": TotalTime}
        }
        self.log_update("Res Codes Updates",
                        ServiceOrder=so,
                        operator=operator,
                        before=before,
                        after=res_code_data)
        sql_command = "UPDATE ServiceOrders SET ResCode=?, BOPTime=?, FOPTime=?, TotalTime=? WHERE ServiceOrder=?"
        return self.execute(sql_command, parameters=(str(res_code_data["ResCodes"]["Code"]),
                                                     res_code_data["ResCodes"]["BOB_time"],
                                                     res_code_data["ResCodes"]["FOP_time"],
                                                     res_code_data["ResCodes"]["Total_time"], so), commit=True)

    def update_comments(self, comments, so, operator):
        current_data = self.select_unit(column='Comments', ServiceOrder=so)
        self.log_update("Updated Location",
                        ServiceOrder=so,
                        operator=operator,
                        before=current_data,
                        after=comments)
        sql_command = "UPDATE ServiceOrders SET Comments=? WHERE ServiceOrder=?"
        return self.execute(sql_command, parameters=(comments, so), commit=True)

    def update_status_updated(self, last_updated, so, operator):
        current_data = self.select_unit(column='Status', ServiceOrder=so)
        self.log_update("Updated Location",
                        ServiceOrder=so,
                        operator=operator,
                        before=current_data,
                        after=last_updated)
        sql_command = "UPDATE ServiceOrders SET Status=? WHERE ServiceOrder=?"
        return self.execute(sql_command, parameters=(last_updated, so), commit=True)

    def update_checked_out(self, checked_out, so, operator):
        current_data = self.select_unit(column='CheckedOut', ServiceOrder=so)
        self.log_update("Checkout",
                        ServiceOrder=so,
                        operator=operator,
                        before=current_data,
                        after=checked_out)
        sql_command = "UPDATE ServiceOrders SET CheckedOut=? WHERE ServiceOrder=?"
        return self.execute(sql_command, parameters=(checked_out, so), commit=True)

    def get_service_orders_by_last_digits(self, last_digits: str):

        sql_command = f"SELECT * FROM ServiceOrders WHERE ServiceOrder LIKE ?"
        return self.execute(sql_command, parameters=('%' + last_digits,), fetchall=True)

    def select_unit(self, column='*', **kwargs):
        sql_command = f"SELECT {column} FROM ServiceOrders WHERE"
        sql_command, parameters = self.format_args(sql_command, kwargs)
        return self.execute(sql_command, parameters=parameters, fetchall=True)

    def delete_service_order(self, status, so, operator):
        current_data = self.select_unit(column='CFI', ServiceOrder=so)
        self.log_update("Delete Service Order",
                        ServiceOrder=so,
                        operator=operator,
                        before={"CFI": current_data},
                        after={"CFI": status})
        sql_command = "UPDATE ServiceOrders SET CFI = 'YES' WHERE ServiceOrder=?"
        return self.execute(sql_command, parameters=(so,), commit=True)

    @staticmethod
    def log_update(operation, operator=None, ServiceOrder=None, before=None, after=None):
        if after is None:
            after = {}
        if before is None:
            before = {}
        print(after)
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = {
            "timestamp": timestamp,
            "operation": operation,
            "operator": operator,
            "changes": {}
        }

        for key, value in after.items():
            change = {
                "before": before.get(key, None),
                "after": value
            }
            log_entry["changes"][key] = change

        log_filename = "update_log.json"

        if os.path.exists(log_filename):
            with open(log_filename, "r") as log_file:
                data = json.load(log_file)
        else:
            data = {}

        service_order_key = str(ServiceOrder)

        if service_order_key not in data:
            data[service_order_key] = []

        data[service_order_key].append(log_entry)
        with open(log_filename, "w") as log_file:
            json.dump(data, log_file, indent=4)

    @staticmethod
    def format_args(sql_command, parameters: dict):

        sql_command += " AND ".join([
            f" {item} =?" for item in parameters
        ])

        return sql_command, tuple(parameters.values())


