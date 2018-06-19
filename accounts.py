from datetime import datetime
from inherit_parent import Inherit


class Account(Inherit):
    """loads provided account details into the object with ability to run the functions below on the object accordingly
    """

    def __init__(self, account_id=None):
        """initialises account object with all attributes"""
        def _get_active_item_condition(cmd, start_date_pos):
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
                "SELECT * FROM accounts_discounts WHERE account_id = {0}".format(account_id), 3)
            spending_limit = _get_active_item_condition(
                "SELECT * FROM accounts_spending_limit WHERE account_id = {0}".format(account_id), 3)
            sub_zero_allowance = _get_active_item_condition(
                "SELECT * FROM accounts_sub_zero_allowance WHERE account_id = {0}".format(account_id), 2)
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

        self._run_condition_delete_commands("accounts_discounts", self.account_id, date=date)

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

        self._run_condition_delete_commands("accounts_spending_limit", self.account_id, date=date)

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

        self._run_condition_delete_commands("accounts_sub_zero_allowance", self.account_id, date=date)

    def update_details(self, **details):
        """updates details passed (raises an error if an unknown detail is passed)"""

        if len(details) == 0:
            raise KeyError("update_details requires at least one argument")

        for key, value in details.items():
            if key == "f_name":
                self._update_item("accounts_f_name", value, str)
                self.f_name = value
            elif key == "l_name":
                self._update_item("accounts_l_name", value, str)
                self.l_name = value
            elif key == "balance":
                self._update_item("accounts_top_ups", value, int, float)
                new_balance = self.balance + value
                self._db_execute("UPDATE accounts SET balance = {0} WHERE account_ID = {1}".format(new_balance,
                                                                                                   self.account_id))
                self.balance = new_balance
            elif key == "notes":
                self._update_item("accounts_notes", value, str)
                self.notes = value
            else:
                raise KeyError("{0} is not a valid detail name. "
                               "Ensure detail name is in [f_name, l_name, balance, notes].".format(key))

    def _update_item(self, table, value, *type_):
        """internal use only - updates given table with given value (only used on standard items that don't have a
        delete option)"""

        if not any(isinstance(value, type__) for type__ in type_):
            raise ValueError("{0} must be an instance of one of the following {1}".format(value, type_))

        self._db_execute("INSERT INTO {0} VALUES (?, ?, ?)".format(table), (self.account_id, value, datetime.now()))

    def _check_item_exists(self, cmd, account_check=True):
        """internal use only - overriding parent class to include a check for account_id being None"""

        if account_check:
            if self.account_id is None:
                return False

        return super()._check_item_exists(cmd)

    def _check_param_validity(self, amount, start_date, end_date, void=None):
        """internal use only - overriding parent class to include a check if account exists"""

        if not self._check_item_exists("SELECT * FROM accounts WHERE account_id = {0}".format(self.account_id)):
            raise ValueError("Account is either set to None or does not exist in database")

        return super()._check_param_validity(amount, start_date, end_date, void)


if __name__ == "__main__":  # test commands
    def _date(date_time):
        return datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S")

    def _date2(date_time):  # with microsecond
        return datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S.%f")

    couch = Account()
    couch.add_account("Couch", "Master")

    couch = Account(1)

    couch.update_details(f_name="Couche")
    couch.update_details(l_name="Lord")
    couch.update_details(l_name="Lord")
    couch.update_details(notes="Testing some new designs out.")
    couch.update_details(balance=100)

    couch.add_discount(100, 1, _date('2018-06-10 14:38:30'), _date('2018-06-30 14:38:30'))
    # couch.delete_discount("2018-06-19 14:50:21.371553")

    couch.add_spending_limit(20, "week", _date('2018-06-10 14:38:30'), _date('2018-06-24 14:38:30'))
    # couch.delete_spending_limit(20, "week", date('2018-06-18 14:38:30'), date('2018-06-18 14:38:30'))

    couch.add_sub_zero_allowance(5, _date('2018-06-11 14:38:30'), _date('2018-06-27 14:38:30'))
    # couch.delete_sub_zero_allowance(5, date('2018-06-18 14:38:30'), date('2018-06-18 14:38:30'))

    couch.delete_account()

    # Note:

    # Adding an account that does NOT exist will run without error
    # Adding an account that DOES     exist will raise a RuntimeError exception

    # Deleting an account that does NOT exist will raise a RuntimeError exception
    # Deleting an account that does     exist will run without error (even if it is already void)
