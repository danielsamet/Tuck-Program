from datetime import datetime
import sqlite3


class Account:
    """loads provided account details into the object with ability to run the functions below on the object accordingly
    """

    def __init__(self, account_id=None):
        """initialises account object with all attributes"""

        if account_id is not None:
            self.account_id = account_id
            self._check_account_is_valid("(so you expect me to load this account how exactly?)")

            account = self._db_execute("SELECT * FROM accounts WHERE account_id = {0}".format(account_id))[0]
            discount = self._db_execute("SELECT * FROM accounts_discounts WHERE account_id = {0}".format(account_id))
            spending_limit = \
                self._db_execute("SELECT * FROM accounts_spending_limit WHERE account_id = {0}".format(account_id))
            sub_zero_allowance = \
                self._db_execute("SELECT * FROM accounts_sub_zero_allowance WHERE account_id = {0}".format(account_id))
        else:
            account = [int(), "", "", 0, "", datetime.now(), False]
            discount, spending_limit, sub_zero_allowance = None, None, None

        self.account_id = account_id
        self.f_name = account[1]
        self.l_name = account[2]
        try:
            self.balance = float(account[3])
        except ValueError:
            self.balance = float()
        self.discount = discount
        self.spending_limit = spending_limit
        self.sub_zero_allowance = sub_zero_allowance
        self.notes = account[4]
        self.date_created = account[5]
        self.void = account[6]

    def add_account(self, f_name, l_name, notes=""):
        """adds account to database with only name parameters"""

        if self.account_id is not None:
            raise ValueError("cannot add an account that already exists! (if account is new then ensure to leave "
                             "account_id empty else if account is simply void then just update the void attrib and run"
                             " update_account)")

        self._db_execute("INSERT INTO accounts VALUES (NULL, ?, ?, ?, ?, ?, ?)",
                         (f_name, l_name, notes, 0, datetime.now(), 0))

        self.account_id, self.f_name, self.l_name, self.notes = self._get_last_id("accounts"), f_name, l_name, notes

    def delete_account(self):
        """deletes account from database using account_id"""

        self._check_account_is_valid("(so you expect me to delete the account how exactly?)")

        # self._db_execute("DELETE FROM accounts WHERE account_ID = {0}".format(self.account_id))

        self.void = False
        self.update_account()

    def update_account(self):
        """updates account in database with any new data"""
        # note: cannot just run the delete and add functions as the database could have related records for the account,
        # e.g. discounts

        self._check_account_is_valid("(so you expect me to update the account how exactly?)")

        self._db_execute("UPDATE accounts SET first_name=\"{0}\", last_name=\"{1}\", balance=\"{2}\", notes=\"{3}\", "
                         "void={4} WHERE account_id={5}".format(self.f_name, self.l_name, self.balance, self.notes,
                                                                1 if self.void else 0, self.account_id))

    def update_balance(self, amount):
        """updates balance in database"""

        self._check_account_is_valid("(so you expect me to update the account account balance how exactly?)")
        try:
            amount = float(amount)
        except ValueError:
            raise ValueError("the amount parameter kinda needs to be a real float")

        self._db_execute("INSERT INTO accounts_top_ups VALUES (?, ?, ?)", (self.account_id, amount,
                                                                           datetime.now().replace(microsecond=0)))
        self.balance += amount
        self.update_account()

    def add_discount(self, amount, type_, start_date, end_date, void=False):
        """adds new discount to database for the account to be applied to all purchases by account"""

        self._discount_validity("add", amount, type_, start_date, end_date, void)

        get_accounts = "SELECT * FROM accounts_discounts WHERE account_id = {0} AND amount = {1} AND type = {2} AND " \
                       "start_date = \"{3}\" AND end_date = \"{4}\"".format(self.account_id, amount, type_, start_date,
                                                                            end_date)
        update_void = "UPDATE accounts_discounts SET void = 0 WHERE account_id = {0} AND amount = {1} AND type = " \
                      "{2} AND start_date = \"{3}\" AND end_date = \"{4}\"".format(self.account_id, amount, type_,
                                                                                   start_date, end_date)
        add_new = ["INSERT INTO accounts_discounts VALUES (?, ?, ?, ?, ?, ?)", (self.account_id, amount, type_,
                                                                                start_date, end_date, 1 if void else 0)]

        self._run_condition_insert_commands(get_accounts, void, update_void, add_new, "discount")

    def delete_discount(self, amount, type_, start_date, end_date):
        """deletes discount from database for the account"""

        self._discount_validity("delete", amount, type_, start_date, end_date)

        self._run_condition_delete_commands("accounts_discounts", amount=amount, type=type_,
                                            start_date="{0}".format(start_date), end_date="{0}".format(end_date))

    def _discount_validity(self, caller, amount, type_, start_date, end_date, void=None):
        """internal use only - runs the parameter validity checks overlapping by the add and delete functions"""

        missing_account_msg = "(so you expect me to {0} a discount how exactly?)".format(caller)
        start_date, end_date = self._check_param_validity(missing_account_msg, amount, start_date, end_date, void)
        if not isinstance(type_, int):
            raise ValueError("type_ parameter must be an int object")

        return start_date, end_date

    def add_spending_limit(self, amount, per, start_date, end_date, void=False):
        """adds spending limit to database for the account"""

        start_date, end_date = self._spending_limit_validity("add", amount, per, start_date, end_date, void)

        get_accounts_cmd = \
            "SELECT * FROM accounts_spending_limit WHERE account_id = {0} AND amount = {1} AND per = \"{2}\" AND " \
            "start_date = \"{3}\" AND end_date = \"{4}\"".format(self.account_id, amount, per, start_date, end_date)
        update_void_cmd = \
            "UPDATE accounts_spending_limit SET void = 0 WHERE account_id = \"{0}\" AND amount = \"{1}\" AND per =" \
            " \"{2}\" AND start_date = \"{3}\" AND end_date = \"{4}\"".format(self.account_id, amount, per, start_date,
                                                                              end_date)
        add_new_cmd = \
            "INSERT INTO accounts_spending_limit VALUES (?, ?, ?, ?, ?, ?)", (self.account_id, amount, per, start_date,
                                                                              end_date, 1 if void else 0)

        self._run_condition_insert_commands(get_accounts_cmd, void, update_void_cmd, add_new_cmd, "spending limit")

    def delete_spending_limit(self, amount, per, start_date, end_date):
        """deletes spending limit from database for the account"""

        start_date, end_date = self._spending_limit_validity("delete", amount, per, start_date, end_date)

        self._run_condition_delete_commands("accounts_spending_limit", amount=amount, per="{0}".format(per),
                                            start_date="{0}".format(start_date), end_date="{0}".format(end_date))

    def _spending_limit_validity(self, caller, amount, per, start_date, end_date, void=None):
        """internal use only - runs the parameter validity checks overlapping by the add and delete functions"""

        missing_account_msg = "(so you expect me to {0} a spending limit how exactly?)".format(caller)  # formats
        # message for either adding or deleting
        start_date, end_date = self._check_param_validity(missing_account_msg, amount, start_date, end_date, void)
        if not isinstance(per, str):
            raise ValueError("per parameter must be an str object")
        elif per not in ['day', 'week', 'month', 'year']:
            raise ValueError("per parameter must be one of the following options: ['day', 'week', 'month', 'year']")

        return start_date, end_date

    def add_sub_zero_allowance(self, amount, start_date, end_date, void=False):
        """adds sub-zero allowance to database for the account"""

        start_date, end_date = self._sub_zero_allowance_validity("add", amount, start_date, end_date, void)

        get_accounts = "SELECT * FROM accounts_sub_zero_allowance WHERE account_id = {0} AND amount = {1} AND " \
                       "start_date = \"{2}\" AND end_date = \"{3}\"".format(self.account_id, amount, start_date,
                                                                            end_date)
        update_void = "UPDATE accounts_sub_zero_allowance SET void = 0 WHERE account_id = \"{0}\" AND amount = " \
                      "\"{1}\" AND start_date = \"{2}\" AND end_date = \"{3}\"".format(self.account_id, amount,
                                                                                       start_date, end_date)
        add_new = "INSERT INTO accounts_sub_zero_allowance VALUES (?, ?, ?, ?, ?)", (self.account_id, amount,
                                                                                     start_date, end_date,
                                                                                     1 if void else 0)

        self._run_condition_insert_commands(get_accounts, void, update_void, add_new, "sub zero allowance")

    def delete_sub_zero_allowance(self, amount, start_date, end_date):
        """deletes sub-zero allowance from database for the account"""

        start_date, end_date = self._sub_zero_allowance_validity("add", amount, start_date, end_date)

        self._run_condition_delete_commands("accounts_sub_zero_allowance", amount=amount,
                                            start_date="{0}".format(start_date), end_date="{0}".format(end_date))

    def _sub_zero_allowance_validity(self, caller, amount, start_date, end_date, void=None):
        """internal use only - runs the parameter validity checks overlapping by the add and delete functions"""

        missing_account_msg = "(so you expect me to {0} a sub zero allowance how exactly?)".format(caller)  # formats
        # message for either adding or deleting
        start_date, end_date = self._check_param_validity(missing_account_msg, amount, start_date, end_date, void)

        return start_date, end_date

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

    def _check_account_is_valid(self, msg):
        """internal use only - checks account_id both exists and is in database"""

        if self.account_id is None:
            raise ValueError("account_id is not currently set {0}".format(msg))
        else:
            if len(self._db_execute("SELECT * FROM accounts WHERE account_id = {0}".format(self.account_id))) == 0:
                raise ValueError("account_id not in database {0}".format(msg))

    def _check_item_exists(self, table, ):

        self._db_execute("SELECT * FROM {0} WHERE account_id = {1}, ") ####

    def _get_last_id(self, table):
        """internal use only - returns the last id used in database"""

        ids = self._db_execute("SELECT account_id FROM {0}".format(table))

        return ids[-1][0]

    def _check_param_validity(self, missing_account_msg, amount, start_date, end_date, void=None):
        """internal use only - checks parameters are instances of the correct objects and returns formatted start and
        end dates"""

        self._check_account_is_valid(missing_account_msg)

        # check parameter validity
        if not isinstance(amount, int):
            raise ValueError("amount parameter must be an int object")
        if not isinstance(start_date, datetime) or not isinstance(end_date, datetime):
            raise ValueError("dates must be passed as datetime.datetime objects")
        if void is not None:
            if not isinstance(void, bool):
                raise ValueError("\"void\" parameter must be from object class \"bool\"")

        return start_date.replace(microsecond=0), end_date.replace(microsecond=0)  # date formatting

    def _run_condition_insert_commands(self, get_accounts, void, update_void, add_new, caller):
        """internal use only - runs insert commands for time-bound item conditions (e.g. adding discount)"""

        discount = self._db_execute(get_accounts)
        if len(discount) == 1:
            if not void and discount[0][-1] == 1:  # if updating void status
                print(1)
                self._db_execute(update_void)
                return
            else:
                raise RuntimeError("A {0} with those parameters already exists (and is not void)!".format(caller))

        self._db_execute(add_new[0], *add_new[1:])

    def _run_condition_delete_commands(self, table, **primary_key):
        """internal use only - runs delete commands for time-bound item conditions (e.g. deleting discount)"""

        sql_command = "UPDATE {0} SET void = 1 WHERE account_id = {1} AND ".format(table, self.account_id)
        sql_command += ' AND '.join(['{} = {!r}'.format(k, v) for k, v in primary_key.items()])

        # print(sql_command)

        self._db_execute(sql_command)


if __name__ == "__main__":  # test commands
    def date(date_time):
        return datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S")

    couch = Account()
    couch.add_account("Couch", "Master")

    couch = Account(1)

    couch.notes = "Hello, happy testing!"
    couch.update_account()

    couch.update_balance(100)

    couch.add_discount(100, 1, date('2018-06-18 14:38:30'), date('2018-06-18 14:38:30'))
    couch.delete_discount(100, 1, date('2018-06-18 14:38:30'), date('2018-06-18 14:38:30'))

    couch.delete_spending_limit(20, "week", date('2018-06-18 14:38:30'), date('2018-06-18 14:38:30'))
    couch.add_spending_limit(20, "week", date('2018-06-18 14:38:30'), date('2018-06-18 14:38:30'))
    couch.delete_spending_limit(20, "week", date('2018-06-18 14:38:30'), date('2018-06-18 14:38:30'))

    couch.add_sub_zero_allowance(5, date('2018-06-18 14:38:30'), date('2018-06-18 14:38:30'))
    couch.delete_sub_zero_allowance(5, date('2018-06-18 14:38:30'), date('2018-06-18 14:38:30'))

    # couch.delete_account()
