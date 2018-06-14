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

        self.void = True
        self.update_account()

    def update_account(self):
        """updates account in database with any new data"""
        # note: cannot just run the delete and add functions as the database could have related records for the account,
        # e.g. discounts

        self._check_account_is_valid("(so you expect me to update the account how exactly?)")

        self._db_execute("UPDATE accounts SET first_name=\"{0}\", last_name=\"{1}\", balance=\"{2}\", notes=\"{3}\", "
                         "void=\"{4}\" WHERE account_id={5}".format(self.f_name, self.l_name, self.balance, self.notes,
                                                                    self.void, self.account_id))

    def update_balance(self, amount):
        """updates balance in database"""

        self._check_account_is_valid("(so you expect me to update the account account balance how exactly?)")
        try:
            amount = float(amount)
        except ValueError:
            raise ValueError("the amount parameter kinda needs to be a real float")

        self._db_execute("INSERT INTO accounts_top_ups VALUES (?, ?, ?)", (self.account_id, amount, datetime.now()))
        self.balance += amount
        self.update_account()

    def add_discount(self, amount, type_, start_date, end_date, void=False):
        """adds new discount to database for the account to be applied to all purchases by account; returns false if
        discount already exists and not void"""

        if not isinstance(start_date, datetime) or not isinstance(end_date, datetime):  # ensure datetime object is used
            raise ValueError("dates must be passed as datetime.datetime objects")
        start_date, end_date = start_date.replace(microsecond=0), end_date.replace(microsecond=0)

        self._check_account_is_valid("(so you expect me to add a discount how exactly?)")

        discount = self._db_execute("SELECT * FROM accounts_discounts WHERE account_id = {0} AND amount = {1} AND "
                                    "start_date = \"{2}\" AND end_date = \"{3}\"".format(self.account_id, amount,
                                                                                         start_date, end_date))

        if len(discount) == 1:
            if void and not discount[-1]:  # if updating void status
                self._db_execute("UPDATE accounts_discounts SET void=TRUE WHERE account_id={0} AND amount={1} AND "
                                 "start_date=\"{2}\" AND end_date=\"{3}\"".format(self.account_id, amount, start_date,
                                                                                  end_date))
            else:
                return False

        self._db_execute("INSERT INTO accounts_discounts VALUES (?, ?, ?, ?, ?, ?)", (self.account_id, amount, type_,
                                                                                      start_date, end_date, void))

        return True

    def delete_discount(self, amount, start_date, end_date):
        """deletes discount from database for the account"""

        self._check_account_is_valid("(so you expect me to delete the discount how exactly?)")

        self._db_execute("UPDATE accounts_discounts SET void=FALSE WHERE account_id = {0} AND amount = {1} AND "
                         "start_date = \"{2}\" AND end_date = \"{3}\"".format(self.account_id, amount, start_date,
                                                                              end_date))

    def add_spending_limit(self, amount, start_date, end_date, void=False):
        """adds spending limit to database for the account"""

        if not isinstance(start_date, datetime) or not isinstance(end_date, datetime):  # ensure datetime object is used
            raise ValueError("dates must be passed as datetime.datetime objects")
        start_date, end_date = start_date.replace(microsecond=0), end_date.replace(microsecond=0)

        self._check_account_is_valid("(so you expect me to add a spending limit how exactly?)")

        spending_limit = self._db_execute("SELECT * FROM accounts_spending_limit WHERE account_id = {0} AND "
                                          "amount = {1} AND start_date = \"{2}\" AND end_date = \"{3}\""
                                          "".format(self.account_id, amount, start_date, end_date))

        if len(spending_limit) == 1:
            if void and not spending_limit[-1]:  # if updating void status
                self._db_execute("UPDATE accounts_spending_limit SET void = TRUE WHERE account_id = \"{0}\" AND "
                                 "amount = \"{1}\" AND start_date = \"{2}\" AND end_date = \"{3}\""
                                 "".format(self.account_id, amount, start_date, end_date))
            else:
                return False

        self._db_execute("INSERT INTO accounts_spending_limit VALUES (?, ?, ?, ?, ?)", (self.account_id, amount,
                                                                                        start_date, end_date, void))

    def delete_spending_limit(self, amount, start_date, end_date):
        """deletes spending limit from database for the account"""

        self._check_account_is_valid("(so you expect me to delete the spending limit how exactly?)")

        self._db_execute("UPDATE accounts_spending_limit SET void = FALSE WHERE account_id = {0} AND amount = {1} AND "
                         "start_date = \"{2}\" AND end_date = \"{3}\"".format(self.account_id, amount, start_date,
                                                                              end_date))

    def add_sub_zero_allowance(self):
        """adds sub-zero allowance to database for the account"""

        pass

    def delete_sub_zero_allowance(self):
        """deletes sub-zero allowance from database for the account"""

        pass

    def _db_open(self, database_name, foreign_keys=True):
        """internal use only - opens connections to database"""

        connection = sqlite3.connect(database_name)
        cursor = connection.cursor()
        if foreign_keys:
            cursor.execute("PRAGMA foreign_keys = 1")
        return connection, cursor

    def _db_execute(self, sql_command, *parameters):
        """internal use only - executes commands on database and returns results"""

        print(sql_command)

        connection, cursor = self._db_open("tuck.db")

        cursor.execute(sql_command, *parameters)
        connection.commit()
        results = cursor.fetchall()

        cursor.close(), connection.close()

        return results

    def _check_account_is_valid(self, msg, ):
        """internal use only - checks account_id both exists and is in database"""

        if self.account_id is None:
            raise ValueError("account_id is not currently set {0}".format(msg))
        else:
            if len(self._db_execute("SELECT * FROM accounts WHERE account_id = {0}".format(self.account_id))) == 0:
                raise ValueError("account_id not in database {0}".format(msg))

    def _get_last_id(self, table):
        """internal use only - returns the last id used in database"""

        ids = self._db_execute("SELECT account_id FROM {0}".format(table))

        return ids[-1][0]


if __name__ == "__main__":
    couch = Account()
    couch.add_account("Couch", "Master")
    # couch = Account(1)
    couch.notes = "Hello, happy testing!"
    couch.update_account()
    couch.update_balance(100)
    couch.add_discount(100, 1, datetime.now(), datetime.now())
    couch.add_spending_limit(20, datetime.now(), datetime.now())
    # couch.add_account("", "")
    # couch.delete_account()
