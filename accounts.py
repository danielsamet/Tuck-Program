from datetime import datetime
from inherit_parent import Inherit


class Account(Inherit):
    """loads provided account details into the object with ability to run the functions below on the object accordingly
    """

    def __init__(self, account_id=None):
        """initialises account object with all attributes"""

        self.item_id = []
        self.item_id.append("account_id")

        self.account_id = account_id
        self.item_id.append(account_id)

        if account_id is not None:
            if not self._check_item_exists("SELECT * FROM accounts WHERE account_id = {0}".format(self.account_id)):
                raise ValueError("Account does not exist in database")

            account = self._db_execute("SELECT * FROM accounts WHERE account_id = {0}".format(account_id))[0]
            f_name = self._get_last_by_date("accounts_f_name")
            l_name = self._get_last_by_date("accounts_l_name")
            discount = self._get_active_item_condition(
                "SELECT * FROM accounts_discounts WHERE account_id = {0}".format(account_id), 3)
            spending_limit = self._get_active_item_condition(
                "SELECT * FROM accounts_spending_limit WHERE account_id = {0}".format(account_id), 3)
            sub_zero_allowance = self._get_active_item_condition(
                "SELECT * FROM accounts_sub_zero_allowance WHERE account_id = {0}".format(account_id), 2)
            notes = self._get_last_by_date("accounts_notes")
        else:
            account = [int(), int(), datetime.now(), False]
            f_name, l_name, notes = str(), str(), str()
            discount, spending_limit, sub_zero_allowance = [], [], []

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

        self.item_id.pop(), self.item_id.append(self.account_id)

        self._db_execute("INSERT INTO accounts_f_name VALUES (?, ?, ?)",
                         (self.account_id, f_name, datetime.now()))
        self._db_execute("INSERT INTO accounts_l_name VALUES (?, ?, ?)", (self.account_id, l_name, datetime.now()))
        self._db_execute("INSERT INTO accounts_notes VALUES (?, ?, ?)", (self.account_id, "Account created!",
                                                                         datetime.now()))
        if notes != "":
            self._db_execute("INSERT INTO accounts_notes VALUES (?, ?, ?)", (self.account_id, notes, datetime.now()))

    def delete_account(self):
        """deletes account from database using account_id"""

        if not self._check_item_exists("SELECT * FROM accounts WHERE account_id = {0}".format(self.account_id)):
            raise ValueError("Account is either set to None or does not exist in database")

        self._db_execute("UPDATE accounts SET void = 1 WHERE account_id = {0}".format(self.account_id))
        self.void = True

    def add_discount(self, amount, type_, start_date, end_date, void=False):
        """adds new discount to database for the account"""

        Inherit._add_discount(self, "accounts", amount, type_, start_date, end_date, void)

    def delete_discount(self, date):
        """deletes discount from database for the account"""

        self._run_condition_delete_commands("accounts_discounts", date=date)

    def add_spending_limit(self, amount, per, start_date, end_date, void=False):
        """adds spending limit to database for the account"""

        Inherit._add_limit(self, "accounts_spending_limit", amount, per, start_date, end_date, void)

    def delete_spending_limit(self, date):
        """deletes spending limit from database for the account"""

        self._run_condition_delete_commands("accounts_spending_limit", date=date)

    def add_sub_zero_allowance(self, amount, start_date, end_date, void=False):
        """adds sub-zero allowance to database for the account"""

        start_date, end_date = self._check_param_validity(amount, start_date, end_date, void)

        get_accounts = \
            "SELECT * FROM accounts_sub_zero_allowance WHERE account_id = {0} AND amount = {1} AND start_date = " \
            "\"{2}\" AND end_date = \"{3}\"".format(self.account_id, amount, start_date, end_date)
        update_void = \
            "UPDATE accounts_sub_zero_allowance SET void = 0 WHERE account_id = \"{0}\" AND amount = \"{1}\" AND " \
            "start_date = \"{2}\" AND end_date = \"{3}\"".format(self.account_id, amount, start_date, end_date)
        add_new = "INSERT INTO accounts_sub_zero_allowance VALUES (?, ?, ?, ?, ?, ?)", \
                  (self.account_id, amount, start_date, end_date, 1 if void else 0, datetime.now())

        self._run_condition_insert_commands(get_accounts, void, update_void, add_new, "sub zero allowance")

    def delete_sub_zero_allowance(self, date):
        """deletes sub-zero allowance from database for the account"""

        self._run_condition_delete_commands("accounts_sub_zero_allowance", date=date)

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
                # self._update_item("accounts_top_ups", value, int, float)  # new top_up function added for topping up
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

    def top_up(self, amount):
        """tops up account with specified amount (as opposed to using the update_details function to update balance
        upon a transaction)"""

        self._update_item("accounts_top_ups", amount, int, float)
        new_balance = self.balance + amount
        self._db_execute("UPDATE accounts SET balance = {0} WHERE account_ID = {1}".format(new_balance,
                                                                                           self.account_id))

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
    couch.add_account("Couch", "Lord")

    # couch = Account(1)

    couch.update_details(l_name="Master")
    couch.update_details(notes="Testing some new designs out.")
    couch.update_details(balance=100)

    couch.add_discount(5, 1, _date('2018-06-10 14:38:30'), _date('2018-07-25 14:38:30'))
    # couch.delete_discount("2018-06-19 14:50:21.371553")

    couch.add_spending_limit(20, "transaction", _date('2018-06-10 14:38:30'), _date('2018-06-24 14:38:30'))
    # couch.delete_spending_limit(20, "week", date('2018-06-18 14:38:30'), date('2018-06-18 14:38:30'))

    couch.add_sub_zero_allowance(5, _date('2018-06-11 14:38:30'), _date('2018-06-27 14:38:30'))
    # couch.delete_sub_zero_allowance(5, date('2018-06-18 14:38:30'), date('2018-06-18 14:38:30'))

    # couch.delete_account()

    # Note:

    # Adding an account that does NOT exist will run without error
    # Adding an account that DOES     exist will raise a RuntimeError exception

    # Deleting an account that does NOT exist will raise a RuntimeError exception
    # Deleting an account that does     exist will run without error (even if it is already void)
