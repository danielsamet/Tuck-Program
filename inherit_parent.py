import sqlite3
from datetime import datetime


class Inherit:
    """this class is designed purely for code sharing amongst different classes to reduce code duplication - not
    intended to be instantiated by itself"""

    def _db_open(self, database_name, foreign_keys=True):
        """internal use only - opens connections to database"""

        connection = sqlite3.connect(database_name)
        cursor = connection.cursor()
        if foreign_keys:
            cursor.execute("PRAGMA foreign_keys = 1")

        return connection, cursor

    def _db_execute(self, sql_command, *parameters):
        """internal use only - executes commands on database and returns results"""

        connection, cursor = self._db_open("tuck.db")

        try:
            cursor.execute(sql_command, *parameters)
        except ValueError:
            raise ValueError("operation parameter must be str \n(sql_command={0}, \nparameters={1})".format(sql_command,
                                                                                                            parameters))
        connection.commit()
        results = cursor.fetchall()

        cursor.close(), connection.close()

        return results

    def _check_item_exists(self, cmd):
        """internal use only - checks item exists in database"""

        if len(self._db_execute(cmd)) == 0:
            return False

        return True

    def _check_param_validity(self, amount, start_date, end_date, void=None):
        """internal use only - checks parameters are instances of the correct objects and returns formatted start and
        end dates"""

        # check parameter validity
        if not isinstance(amount, int):
            raise ValueError("amount parameter must be an int object")
        if not isinstance(start_date, datetime) or not isinstance(end_date, datetime):
            raise ValueError("dates must be passed as datetime.datetime objects")
        if void is not None:
            if not isinstance(void, bool):
                raise ValueError("\"void\" parameter must be from object class \"bool\"")

        return start_date.replace(microsecond=0), end_date.replace(microsecond=0)  # date formatting

    def _get_last_id(self, table):
        """internal use only - returns the last id used in database"""

        column_name = self._db_execute("PRAGMA TABLE_INFO({0})".format(table))[0][1]
        ids = self._db_execute("SELECT {0} FROM {1}".format(column_name, table))

        return ids[-1][0]

    def _run_condition_insert_commands(self, get_items, void, update_void, add_new, caller):
        """internal use only - runs insert commands for time-bound item conditions (e.g. adding discount)"""

        item = self._db_execute(get_items)
        if len(item) == 1:
            if not void and item[0][-1] == 1:  # if updating void status
                self._db_execute(update_void)
                return
            else:
                raise RuntimeError("A {0} with those parameters already exists (and is not void)!".format(caller))

        self._db_execute(add_new[0], *add_new[1:])

    def _run_condition_delete_commands(self, table, item_id, **primary_key):
        """internal use only - runs delete commands for time-bound item conditions (e.g. deleting discount)"""

        where_clause = ' AND '.join(['{} = {!r}'.format(key, value) for key, value in primary_key.items()])  # see
        # printed sql_command to understand this line

        if not self._check_item_exists("SELECT * FROM {0} WHERE account_id = {1} AND ".format(table, item_id)
                                       + where_clause):
            raise RuntimeError("No time-bound item condition found (e.g. no discount found) matching criteria thus "
                               "cannot be deleted.")

        sql_command = "UPDATE {0} SET void = 1 WHERE account_id = {1} AND ".format(table, item_id)
        sql_command += where_clause

        self._db_execute(sql_command)

    def _get_active_item_condition(self, cmd, start_date_pos):
        """internal use only - returns only those items from the given command that are not void and current date
        is within start and end date"""

        active_items = list()

        item_conditions = self._db_execute(cmd)

        for item in item_conditions:
            if item[-2] == 0:  # if not void
                if datetime.strptime(item[start_date_pos], "%Y-%m-%d %H:%M:%S") < datetime.now() \
                        < datetime.strptime(item[start_date_pos + 1], "%Y-%m-%d %H:%M:%S"):
                    active_items.append(list(item[:start_date_pos]) + [int(i) for i in str(item[-2])])  # no cleaner
                    # method to concatenate when slice is int

        return active_items

    def _get_last_by_date(self, table, **item_id):
        """internal use only - gets last item entered into table for current account"""

        return self._db_execute("SELECT * FROM {0} WHERE {1} = {2} AND date = "
                                "(SELECT max(date) FROM {0} WHERE {1} = {2})".format(table, list(item_id.keys())[0],
                                                                                     list(item_id.values())[0]))
