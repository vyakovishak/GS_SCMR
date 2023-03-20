import datetime
import json
import sqlite3


class ServiceOrderDB:
    def __init__(self, path_to_db="ServiceOrders.db", status_bar=None):
        self.path_to_db = path_to_db
        self.status_bar = status_bar

    @property
    def connection(self):
        return sqlite3.connect(self.path_to_db)

    def execute(self, sql: str, parameters: tuple = None, fetchone=False, fetchall=False, commit=False):
        if not parameters:
            parameters = tuple()
        connection = self.connection
        cursor = connection.cursor()
        connection.set_trace_callback(logger)
        cursor.execute(sql, parameters)

        data = None
        if commit:
            connection.commit()
        if fetchone:
            data = cursor.fetchone()
        if fetchall:
            data = cursor.fetchall()
        #connection.close()

        return data

    def create_table_users(self):
        sql = """
                CREATE TABLE IF NOT EXISTS ServiceOrders (
                ServiceOrder INTEGER PRIMARY KEY,
                Location VARCHAR(255),
                CompletionDate DATETIME,
                ClosedBy VARCHAR(255),
                Status VARCHAR(255),
                Comments TEXT,
                LastUpdated DATETIME,
                UpdatedBy VARCHAR(255),
                CheckOutBy VARCHAR(255),
                CheckOutDate DATETIME,
                CheckedOut BOOLEAN DEFAULT FALSE
            );"""

        self.execute(sql, commit=True)

    def add_service_order(self,
                          ServiceOrder: int,
                          Location: str,
                          CompletionDate: str,
                          ClosedBy: str,
                          Status: str,
                          Comments: str
                          ):  # 12
        self.log_update("Add Service Order", ServiceOrder=ServiceOrder, Location=Location,
                        CompletionDate=CompletionDate, ClosedBy=ClosedBy, Status=Status, Comments=Comments,
                        )

        SQL_COMMAND = "INSERT OR IGNORE INTO ServiceOrders(ServiceOrder, Location, CompletionDate, ClosedBy, Status, Comments) VALUES(?,?,?,?,?,?)"

        parameters = (ServiceOrder,
                      Location,
                      CompletionDate,
                      ClosedBy,
                      Status,
                      Comments,
                      )

        self.execute(SQL_COMMAND, parameters=parameters, commit=True)

    # ServiceOrderDB.py

    def select_all_unchecked_out(self):
        SQL_COMMAND = "SELECT * FROM ServiceOrders WHERE CheckedOut=0"
        return self.execute(SQL_COMMAND, fetchall=True)

    def update_check_out_by(self, check_out_by, so, operator):
        current_data =  self.select_unit(column='CheckOutBy', ServiceOrder=so)
        self.log_update("Updated Check Out By", so=so, operator=operator, before=current_data, after=check_out_by)
        SQL_COMMAND = "UPDATE ServiceOrders SET CheckOutBy=? WHERE ServiceOrder=?"
        return self.execute(SQL_COMMAND, parameters=(check_out_by, so), commit=True)

    def update_check_out_date(self, check_out_date, so, operator):
        current_data = self.select_unit(column='CheckOutDate', ServiceOrder=so)
        self.log_update("Updated Check Out Date", so=so, operator=operator,before=current_data, after=check_out_date)
        SQL_COMMAND = "UPDATE ServiceOrders SET CheckOutDate=? WHERE ServiceOrder=?"
        return self.execute(SQL_COMMAND, parameters=(check_out_date, so), commit=True)

    def select_all_service_orders(self):
        SQL_COMMAND = "SELECT * FROM ServiceOrders"
        return self.execute(SQL_COMMAND, fetchall=True)

    def update_service_order_number(self, old_so,  operator):
        current_data = self.select_unit(column='ServiceOrder', ServiceOrder=old_so)
        self.log_update("Update Service Order Number",  operator=operator, before=old_so, after=current_data)
        SQL_COMMAND = "UPDATE ServiceOrders SET ServiceOrder=? WHERE ServiceOrder=?"
        return self.execute(SQL_COMMAND, parameters=(new_so, old_so), commit=True)

    def update_location(self, location, so, operator):
        current_data = self.select_unit(column='Location', ServiceOrder=so)
        self.log_update("Updated Location", so=so, operator=operator,before=current_data, after=location)
        SQL_COMMAND = "UPDATE ServiceOrders SET Location=? WHERE ServiceOrder=?"
        return self.execute(SQL_COMMAND, parameters=(location, so), commit=True)

    def update_completion_date(self, completion_date, so, operator):
        current_data = self.select_unit(column='CompletionDate', ServiceOrder=so)
        self.log_update("Updated Location", so=so, operator=operator, before=current_data, after=completion_date)
        SQL_COMMAND = "UPDATE ServiceOrders SET CompletionDate=? WHERE ServiceOrder=?"
        return self.execute(SQL_COMMAND, parameters=(completion_date, so), commit=True)

    def update_closed_by(self, closed_by, so, operator):
        current_data = self.select_unit(column='ClosedBy', ServiceOrder=so)
        self.log_update("Updated Location", so=so, operator=operator, before=current_data, after=closed_by)
        SQL_COMMAND = "UPDATE ServiceOrders SET ClosedBy=? WHERE ServiceOrder=?"
        return self.execute(SQL_COMMAND, parameters=(closed_by, so), commit=True)

    def update_status(self, status, so, operator):
        current_data = self.select_unit(column='Status', ServiceOrder=so)
        self.log_update("Updated Location", so=so, operator=operator, before=current_data, after=status)
        SQL_COMMAND = "UPDATE ServiceOrders SET Status=? WHERE ServiceOrder=?"
        return self.execute(SQL_COMMAND, parameters=(status, so), commit=True)

    def update_comments(self, comments, so, operator):
        current_data = self.select_unit(column='Comments', ServiceOrder=so)
        self.log_update("Updated Location", so=so, operator=operator, before=current_data, after=comments)
        SQL_COMMAND = "UPDATE ServiceOrders SET Comments=? WHERE ServiceOrder=?"
        return self.execute(SQL_COMMAND, parameters=(comments, so), commit=True)

    def update_status_updated(self, last_updated, so, operator):
        current_data = self.select_unit(column='Status', ServiceOrder=so)
        self.log_update("Updated Location", so=so, operator=operator, before=current_data, after=last_updated)
        SQL_COMMAND = "UPDATE ServiceOrders SET Status=? WHERE ServiceOrder=?"
        return self.execute(SQL_COMMAND, parameters=(last_updated, so), commit=True)

    def update_checked_out(self, checked_out, so, operator):
        current_data = self.select_unit(column='CheckedOut', ServiceOrder=so)
        self.log_update("Updated Location", so=so, operator=operator, before=current_data, after=checked_out)
        SQL_COMMAND = "UPDATE ServiceOrders SET CheckedOut=? WHERE ServiceOrder=?"
        return self.execute(SQL_COMMAND, parameters=(checked_out, so), commit=True)

    def select_unit(self, column='*', **kwargs):
        SQL_COMMAND = f"SELECT {column} FROM ServiceOrders WHERE"
        SQL_COMMAND, parameters = self.format_args(SQL_COMMAND, kwargs)
        return self.execute(SQL_COMMAND, parameters=parameters, fetchall=True)

    def count_users(self):
        return self.execute("SELECT COUNT(*) FROM ServiceOrders;", fetchone=True)

    def delete_all_users(self, operator):
        self.log_update("Delete All Service Orders", operator=operator)
        return self.execute("DELETE FROM ServiceOrders WHERE True", commit=True)

    def delete_service_order(self, so, operator):
        self.log_update("Delete Service Order", so=so, operator=operator)
        SQL_COMMAND = "DELETE FROM ServiceOrders WHERE ServiceOrder=?"
        return self.execute(SQL_COMMAND, parameters=(so,), commit=True)

    def log_update(self, operation, **kwargs):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = {
            "timestamp": timestamp,
            "operation": operation,
            "parameters": kwargs
        }
        log_entry_json = json.dumps(log_entry)

        with open("update_log.json", "a") as log_file:
            log_file.write(log_entry_json + "\n")

    @staticmethod
    def format_args(SQL_COMMAND, parameters: dict):

        SQL_COMMAND += " AND ".join([
            f" {item} =?" for item in parameters
        ])

        return SQL_COMMAND, tuple(parameters.values())


def logger(statement):
    print(f"""
------------------------------------
Executing:
{statement}
------------------------------------
""")
