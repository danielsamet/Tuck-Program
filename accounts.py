from datetime import datetime
from inherit_parent import Inherit


class Account(Inherit):
    """loads provided account details into the object with ability to run the functions below on the object accordingly
    """

    def __init__(self, account_id=None):
        """initialises account object with all attributes"""
        def _get_active_item_condition(cmd):
            """internal use only - returns only those items from the given command that are not void and current date
            is within start and end date"""

            active_items = list()

            item_conditions = self._db_execute(cmd)

            for item in item_conditions:
                if item[-1] == 0:  # if not void
                    if datetime.strptime(item[3], "%Y-%m-%d %H:%M:%S") < datetime.now() \
                            < datetime.strptime(item[4], "%Y-%m-%d %H:%M:%S"):
                        active_items.append(item)

            return active_items

        def _get_last_by_date(table):
            """internal use only - gets last item entered into table for current account"""

            return self._db_execute("SELECT * FROM {0} WHERE account_id = {1} AND date = "
                                    "(SELECT max(date) FROM {0} WHERE account_id = {1})".format(table, self.account_id))

        if account_id is not None:
            self.account_id = account_id

            if not self._check_item_exists("SELECT * FROM accounts WHERE account_id = {0}".format(self.account_id)):
                raise ValueError("Account does not exist in database")

            account = self._db_execute("SELECT * FROM accounts WHERE account_id = {0}".format(account_id))[0]
            f_name = _get_last_by_date("accounts_f_name")
            l_name = _get_last_by_date("accounts_l_name")
            discount = _get_active_item_condition(
                "SELECT * FROM accounts_discounts WHERE account_id = {0}".format(account_id))
            spending_limit = _get_active_item_condition(
                "SELECT * FROM accounts_spending_limit WHERE account_id = {0}".format(account_id))
            sub_zero_allowance = _get_active_item_condition(
                "SELECT * FROM accounts_sub_zero_allowance WHERE account_id = {0}".format(account_id))
            notes = _get_last_by_date("accounts_notes")
        else:
            account = [int(), int(), datetime.now(), False]
            f_name, l_name, notes = str(), str(), str()
            discount, spending_limit, sub_zero_allowance = [], [], []

        self.account_id = account_id
        self.f_name = f_name
        self.l_name = l_name
        self.balance = float(account[1])

        self.discount = discount
        self.spending_limit = spending_limit
        self.sub_zero_allowance = sub_zero_allowance

        self.notes = notes
        self.date_created = account[2]
        self.void = account[3]

    def add_account(self, f_name, l_name, notes=""):
        """adds account to database"""

        if self.account_id is not None:
            raise ValueError("cannot add an account that already exists! (if account is new then ensure to leave "
                             "account_id empty else if account is simply void then just update the void attrib and run"
                             " update_account)")

        self._db_execute("INSERT INTO accounts VALUES (NULL, ?, ?, ?)", (0, datetime.now(), 0))

        self.account_id, self.f_name, self.l_name, self.notes = self._get_last_id("accounts"), f_name, l_name, notes

        self._db_execute("INSERT INTO accounts_f_name VALUES (?, ?, ?)",
                         (self.account_id, f_name, datetime.now()))
        self._db_execute("INSERT INTO accounts_l_name VALUES (?, ?, ?)",
                         (self.account_id, l_name, datetime.now()))
        if notes != "":
            self._db_execute("INSERT INTO accounts_notes VALUES (?, ?, ?)",
                             (self.account_id, notes, datetime.now()))

    def delete_account(self):
        """deletes account from database using account_id"""

        if not self._check_item_exists("SELECT * FROM accounts WHERE account_id = {0}".format(self.account_id)):
            raise ValueError("Account is either set to None or does not exist in database")

        self._db_execute("UPDATE accounts SET void = 1 WHERE account_id = {0}".format(self.account_id))
        self.void = False

    def add_discount(self, amount, type_, start_date, end_date, void=False):
        """adds new discount to database for the account to be applied to all purchases by account"""

        start_date, end_date = self._check_param_validity(amount, start_date, end_date, void)
        if not isinstance(type_, int):
            raise ValueError("type_ parameter must be an int object")

        get_accounts = "SELECT * FROM accounts_discounts WHERE account_id = {0} AND amount = {1} AND type = {2} AND " \
                       "start_date = \"{3}\" AND end_date = \"{4}\"".format(self.account_id, amount, type_, start_date,
                                                                            end_date)
        update_void = "UPDATE accounts_discounts SET void = 0 WHERE account_id = {0} AND amount = {1} AND type = " \
                      "{2} AND start_date = \"{3}\" AND end_date = \"{4}\"".format(self.account_id, amount, type_,
                                                                                   start_date, end_date)
        add_new = ["INSERT INTO accounts_discounts VALUES (?, ?, ?, ?, ?, ?, ?)", (self.account_id, amount, type_,
                                                                                   start_date, end_date,
                                                                                   1 if void else 0, datetime.now())]

        self._run_condition_insert_commands(get_accounts, void, update_void, add_new, "discount")

    def delete_discount(self, date):
        """deletes discount from database for the account"""

        self._run_condition_delete_commands("accounts_discounts", date=date)

    def add_spending_limit(self, amount, per, start_date, end_date, void=False):
        """adds spending limit to database for the account"""

        start_date, end_date = self._check_param_validity(amount, start_date, end_date, void)
        if not isinstance(per, str):
            raise ValueError("per parameter must be an str object")
        elif per not in ['day', 'week', 'month', 'year']:
            raise ValueError("per parameter must be one of the following options: ['day', 'week', 'month', 'year']")

        get_accounts_cmd = \
            "SELECT * FROM accounts_spending_limit WHERE account_id = {0} AND amount = {1} AND per = \"{2}\" AND " \
            "start_date = \"{3}\" AND end_date = \"{4}\"".format(self.account_id, amount, per, start_date, end_date)
        update_void_cmd = \
            "UPDATE accounts_spending_limit SET void = 0 WHERE account_id = \"{0}\" AND amount = \"{1}\" AND per =" \
            " \"{2}\" AND start_date = \"{3}\" AND end_date = \"{4}\"".format(self.account_id, amount, per, start_date,
                                                                              end_date)
        add_new_cmd = \
            "INSERT INTO accounts_spending_limit VALUES (?, ?, ?, ?, ?, ?, ?)", (self.account_id, amount, per,
                                                                                 start_date, end_date,
                                                                                 1 if void else 0, datetime.now())

        self._run_condition_insert_commands(get_accounts_cmd, void, update_void_cmd, add_new_cmd, "spending limit")

    def delete_spending_limit(self, date):
        """deletes spending limit from database for the account"""

        self._run_condition_delete_commands("accounts_spending_limit", date=date)

    def add_sub_zero_allowance(self, amount, start_date, end_date, void=False):
        """adds sub-zero allowance to database for the account"""

        start_date, end_date = self._check_param_validity(amount, start_date, end_date, void)

        get_accounts = "SELECT * FROM accounts_sub_zero_allowance WHERE account_id = {0} AND amount = {1} AND " \
                       "start_date = \"{2}\" AND end_date = \"{3}\"".format(self.account_id, amount, start_date,
                                                                            end_date)
        update_void = "UPDATE accounts_sub_zero_allowance SET void = 0 WHERE account_id = \"{0}\" AND amount = " \
                      "\"{1}\" AND start_date = \"{2}\" AND end_date = \"{3}\"".format(self.account_id, amount,
                                                                                       start_date, end_date)
        add_new = "INSERT INTO accounts_sub_zero_allowance VALUES (?, ?, ?, ?, ?, ?)", (self.account_id, amount,
                                                                                        start_date, end_date,
                                                                                        1 if void else 0,
                                                                                        datetime.now())

        self._run_condition_insert_commands(get_accounts, void, update_void, add_new, "sub zero allowance")

    def delete_sub_zero_allowance(self, date):
        """deletes sub-zero allowance from database for the account"""

        self._run_condition_delete_commands("accounts_sub_zero_allowance", date=date)

    def update_account(self):
        """updates account in database with any new data"""
        # note: cannot just run the delete and add functions as the database could have related records for the account,
        # e.g. discounts

        if not self._check_item_exists("SELECT * FROM accounts WHERE account_id = {0}".format(self.account_id)):
            raise ValueError("Account is either set to None or does not exist in database")

        self._db_execute("UPDATE accounts SET first_name=\"{0}\", last_name=\"{1}\", balance=\"{2}\", notes=\"{3}\", "
                         "void={4} WHERE account_id={5}".format(self.f_name, self.l_name, self.balance, self.notes,
                                                                1 if self.void else 0, self.account_id))

    def update_balance(self, amount):
        """updates balance in database"""

        if not self._check_item_exists("SELECT * FROM accounts WHERE account_id = {0}".format(self.account_id)):
            raise ValueError("Account is either set to None or does not exist in database")

        try:
            amount = float(amount)
        except ValueError:
            raise ValueError("the amount parameter kinda needs to be a real float")

        self._db_execute("INSERT INTO accounts_top_ups VALUES (?, ?, ?)", (self.account_id, amount,
                                                                           datetime.now().replace(microsecond=0)))
        self.balance += amount
        self.update_account()

    def _check_item_exists(self, cmd, account_check=True):
        """internal use only - overriding parent class to include a check for account_id being None None"""

        if account_check:
            if self.account_id is None:
                return False

        return super()._check_item_exists(cmd)

    def _check_param_validity(self, amount, start_date, end_date, void=None):
        """internal use only - checks parameters are instances of the correct objects and returns formatted start and
        end dates"""

        if not self._check_item_exists("SELECT * FROM accounts WHERE account_id = {0}".format(self.account_id)):
            raise ValueError("Account is either set to None or does not exist in database")

        # check parameter validity
        if not isinstance(amount, int):
            raise ValueError("amount parameter must be an int object")
        if not isinstance(start_date, datetime) or not isinstance(end_date, datetime):
            raise ValueError("dates must be passed as datetime.datetime objects")
        if void is not None:
            if not isinstance(void, bool):
                raise ValueError("\"void\" parameter must be from object class \"bool\"")

        return start_date.replace(microsecond=0), end_date.replace(microsecond=0)  # date formatting

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

        if not self._check_item_exists("SELECT * FROM {0} WHERE account_id = {1} AND ".format(table, self.account_id)
                                       + where_clause, False):
            raise RuntimeError("No time-bound item condition found (e.g. no discount found) matching criteria thus "
                               "cannot be deleted.")

        sql_command = "UPDATE {0} SET void = 1 WHERE account_id = {1} AND ".format(table, self.account_id)
        sql_command += where_clause

        self._db_execute(sql_command)


if __name__ == "__main__":  # test commands
    def _date(date_time):
        return datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S")

    couch = Account()
    couch.add_account("Couch", "Master")

    # couch = Account(1)
#
    # couch.notes = "Hello, happy testing!"
    # couch.update_account()
#
    # couch.update_balance(100)
#
    # couch.add_discount(100, 1, date('2018-06-18 14:38:30'), date('2018-06-18 14:38:30'))
    # # couch.delete_discount(100, 1, date('2018-06-18 14:38:30'), date('2018-06-18 14:38:30'))
#
    # # couch.delete_spending_limit(20, "week", date('2018-06-18 14:38:30'), date('2018-06-18 14:38:30'))
    # couch.add_spending_limit(20, "week", date('2018-06-18 14:38:30'), date('2018-06-18 14:38:30'))
    # couch.delete_spending_limit(20, "week", date('2018-06-18 14:38:30'), date('2018-06-18 14:38:30'))
#
    # couch.add_sub_zero_allowance(5, date('2018-06-18 14:38:30'), date('2018-06-18 14:38:30'))
    # couch.delete_sub_zero_allowance(5, date('2018-06-18 14:38:30'), date('2018-06-18 14:38:30'))

    # couch.delete_account()

    # Note:

    # Adding an account that does NOT exist will run without error
    # Adding an account that DOES     exist will raise a RuntimeError exception

    # Deleting an account that does NOT exist will raise a RuntimeError exception
    # Deleting an account that does     exist will run without error (even if it is already void)
