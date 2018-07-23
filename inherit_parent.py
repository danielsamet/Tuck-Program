import sqlite3
from datetime import datetime


path = ""


class Inherit:
    """this class is designed purely for code sharing amongst different classes to reduce code duplication - not
    intended to be instantiated by alone"""

    item_id = []  # [item_id_name, item_id]

    def _db_open(self, database_name, foreign_keys=True):
        """internal use only - opens connections to database"""

        connection = sqlite3.connect(database_name)
        cursor = connection.cursor()
        if foreign_keys:
            cursor.execute("PRAGMA foreign_keys = 1")

        return connection, cursor

    def _db_execute(self, sql_command, *parameters):
        """internal use only - executes commands on database and returns results"""

        connection, cursor = self._db_open(path + "\\tuck.db")

        try:
            cursor.execute(sql_command, *parameters)
        except ValueError:
            raise ValueError("operation parameter must be str \n(sql_command={0}, \nparameters={1})".format(sql_command,
                                                                                                            parameters))
        connection.commit()
        results = cursor.fetchall()

        cursor.close(), connection.close()

        return results

    def _check_item_exists(self, cmd, item_check=True):
        """internal use only - checks item exists in database"""

        if item_check:
            if self.item_id[1] is None:
                return False

        if len(self._db_execute(cmd)) == 0:
            return False

        return True

    def _check_param_validity(self, amount, start_date, end_date, void=None):
        """internal use only - checks parameters are instances of the correct objects and returns formatted start and
        end dates"""

        # check parameter validity
        if not isinstance(amount, (int, float)):
            raise ValueError("amount parameter must be an int object")
        if not (isinstance(start_date, datetime) or (isinstance(end_date, datetime) and end_date != "")):
            raise ValueError("dates must be passed as datetime.datetime objects")
        if void is not None:
            if not isinstance(void, bool):
                raise ValueError("\"void\" parameter must be from object class \"bool\"")

        # date formatting
        return start_date.replace(microsecond=0), end_date.replace(microsecond=0) if end_date != "" else end_date

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

    def _run_condition_delete_commands(self, table, **primary_key):
        """internal use only - runs delete commands for time-bound item conditions (e.g. deleting discount)"""

        where_clause = ' AND '.join(['{} = {!r}'.format(key, value) for key, value in primary_key.items()])  # see
        # printed sql_command to understand this line
        check_cmd = "SELECT * FROM {0} WHERE {1} = {2} AND ".format(table, self.item_id[0], self.item_id[1]) \
                    + where_clause

        if not self._check_item_exists(check_cmd):
            raise RuntimeError("No time-bound item condition found (e.g. no discount found) matching criteria thus "
                               "cannot be deleted.")

        sql_command = "UPDATE {0} SET void = 1 WHERE {1} = {2} AND ".format(table, self.item_id[0], self.item_id[1])
        sql_command += where_clause

        self._db_execute(sql_command)

    def _get_active_item_condition(self, cmd, start_date_pos):
        """internal use only - returns only those items from the given command that are not void and current date
        is within start and end date"""

        active_items = list()

        item_conditions = self._db_execute(cmd)

        for item in item_conditions:
            if item[-2] == 0:  # if not void
                if datetime.strptime(item[start_date_pos], "%Y-%m-%d %H:%M:%S") < datetime.now():
                    if item[start_date_pos + 1] != "":  # allows for indefinite item conditions
                        if datetime.now() > datetime.strptime(item[start_date_pos + 1], "%Y-%m-%d %H:%M:%S"):
                            continue

                    active_items.append(list(item[1:start_date_pos]) + [int(i) for i in str(item[-2])])  # no cleaner
                    # method to concatenate when slice is int  # the concatenation is simply for the removal of
                    # unnecessary date

        return active_items

    def _get_last_by_date(self, table):
        """internal use only - gets last item entered into table for current account/product"""

        cmd = "SELECT * FROM {0} WHERE {1} = {2} AND date = (SELECT max(date) FROM {0} WHERE {1} = {2})".format(
            table, self.item_id[0], self.item_id[1])

        return self._db_execute(cmd)

    def _check_type_param(self, type_):
        """internal use only - checks if the type_ parameter is valid"""

        if not isinstance(type_, int):
            raise ValueError("type_ parameter must be an int object")
        valid_types = [0, 1]  # pence, percent
        if type_ not in valid_types:
            raise ValueError("type_ parameter must be in: {0}".format(valid_types))

    def _add_discount(self, caller, amount, type_, start_date, end_date, void=False):
        """internal use only - adds new discount to database for the caller item (e.g. account)"""

        start_date, end_date = self._check_param_validity(amount, start_date, end_date, void)
        self._check_type_param(type_)

        get_items = "SELECT * FROM {0}_discounts WHERE {1} = {2} AND amount = {3} AND type = {4} AND " \
                    "start_date = \"{5}\" AND end_date = \"{6}\"".format(caller, self.item_id[0], self.item_id[1],
                                                                         amount, type_, start_date, end_date)
        update_void = "UPDATE {0}_discounts SET void = 0 WHERE {1} = {2} AND amount = {3} AND type = {4} AND " \
                      "start_date = \"{5}\" AND end_date = \"{6}\"".format(caller, self.item_id[0], self.item_id[1],
                                                                           amount, type_, start_date, end_date)
        add_new = ["INSERT INTO {0}_discounts VALUES (?, ?, ?, ?, ?, ?, ?)".format(caller),
                   (self.item_id[1], amount, type_, start_date, end_date, 1 if void else 0, datetime.now())]

        self._run_condition_insert_commands(get_items, void, update_void, add_new, "discount")

    def _add_limit(self, caller, amount, per, start_date, end_date, void=False):
        """internal use only adds item limit to database"""

        start_date, end_date = self._check_param_validity(amount, start_date, end_date, void)
        if not isinstance(per, str):
            raise ValueError("per parameter must be an str object")
        elif per not in ['transaction', 'day', 'week', 'month', 'year']:
            raise ValueError("per parameter must be one of the following options: ['day', 'week', 'month', 'year']")

        get_items_cmd = \
            "SELECT * FROM {0} WHERE {1} = {2} AND amount = {3} AND per = \"{4}\" AND start_date = \"{5}\" AND " \
            "end_date = \"{6}\"".format(caller, self.item_id[0], self.item_id[1], amount, per, start_date, end_date)
        update_void_cmd = \
            "UPDATE {0} SET void = 0 WHERE {1} = \"{2}\" AND amount = \"{3}\" AND per = \"{4}\" AND start_date = " \
            "\"{5}\" AND end_date = \"{6}\"".format(caller, self.item_id[0], self.item_id[1], amount, per, start_date,
                                                    end_date)
        add_new_cmd = \
            "INSERT INTO {0} VALUES (?, ?, ?, ?, ?, ?, ?)".format(caller), \
            (self.item_id[1], amount, per, start_date, end_date, 1 if void else 0, datetime.now())

        self._run_condition_insert_commands(get_items_cmd, void, update_void_cmd, add_new_cmd, "limit")

    def _update_item(self, table, value, *type_):
        """internal use only - updates given table with given value (only used on standard items that don't have a
        delete option)"""

        if not any(isinstance(value, type__) for type__ in type_):
            raise ValueError("{0} must be an instance of one of the following {1}".format(value, type_))

        self._db_execute("INSERT INTO {0} VALUES (?, ?, ?)".format(table), (self.item_id[1], value, datetime.now()))
