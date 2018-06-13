from datetime import datetime
import sqlite3


class Account:
    """loads provided account details into the object with ability to run the functions below on the object accordingly
    """

    def __init__(self, account_id=None):
        """initialises account object with all attributes"""

        if account_id is not None:
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
        self.balance = account[3]
        self.discount = discount
        self.spending_limit = spending_limit
        self.sub_zero_allowance = sub_zero_allowance
        self.notes = account[4]
        self.date_created = account[5]
        self.void = account[6]

    def add_account(self, f_name, l_name, notes=""):
        """adds account to database with only name parameters"""

        if self.account_id is not None:
            raise ValueError("cannot add an account that already exists! (note: new accounts will be auto-assigned an "
                             "account_ID)")

        self._db_execute("INSERT INTO accounts VALUES (NULL, ?, ?, ?, ?, ?, ?)",
                         (f_name, l_name, notes, 0, datetime.now(), 0))

        self.f_name, self.l_name, self.notes = f_name, l_name, notes

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

        self._db_execute("UPDATE accounts SET first_name=\"{0}\", last_name=\"{1}\", notes=\"{2}\", void=\"{3}\" WHERE "
                         "account_id={4}".format(self.f_name, self.l_name, self.notes, self.void, self.account_id))

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

        self._check_account_is_valid("(so you expect me to add a discount how exactly?)")

        discount = self._db_execute("SELECT * FROM accounts_discounts WHERE account_id = {0} AND amount = {1} AND "
                                    "start_date = {2} AND end_date = {3}".format(self.account_id, amount, start_date,
                                                                                 end_date))

        if len(discount) == 1:
            if void and not discount[-1]:  # if updating void status
                self._db_execute("UPDATE accounts_discounts SET void=TRUE WHERE account_id={0} AND amount={1} AND "
                                 "start_date={2} AND end_date={3}".format(self.account_id, amount, start_date,
                                                                          end_date))
            else:
                return False

        self._db_execute("INSERT INTO accounts_discounts VALUES (?, ?, ?, ?, ?, ?)", (self.account_id, amount, type_,
                                                                                      start_date, end_date, void))

        return True

    def delete_discount(self, amount, start_date, end_date):
        """deletes discount from database for the account"""

        self._check_account_is_valid("(so you expect me to delete the discount how exactly?)")

        self._db_execute("UPDATE accounts_discounts SET void=FALSE WHERE account_id={0} AND amount={1} AND "
                         "start_date={2} AND end_date={3}".format(self.account_id, amount, start_date, end_date))

    def add_spending_limit(self):
        """adds spending limit to database for the account"""

        pass

    def delete_spending_limit(self):
        """deletes spending limit from database for the account"""

        pass

    def add_sub_zero_allowance(self):
        """adds sub-zero allowance to database for the account"""

        pass

    def delete_sub_zero_allowance(self):
        """deletes sub-zero allowance from database for the account"""

        pass

    def _db_opener(self, database_name, foreign_keys=True):
        """internal use only - opens connections to database"""

        connection = sqlite3.connect(database_name)
        cursor = connection.cursor()
        if foreign_keys:
            cursor.execute("PRAGMA foreign_keys = 1")
        return connection, cursor

    def _db_execute(self, sql_command, *parameters):
        """internal use only - executes commands on database and returns results"""

        connection, cursor = self._db_opener("tuck.db")

        cursor.execute(sql_command, *parameters)
        connection.commit()
        results = cursor.fetchall()

        cursor.close(), connection.close()

        return results

    def _check_account_is_valid(self, msg):
        """internal use only - checks account_id both exists and is in database"""

        if self.account_id is None:
            raise ValueError("account_id is not currently set {0}".format(msg))
        else:
            if len(self._db_execute("SELECT * FROM accounts WHERE account_id = {0}".format(self.account_id))) == 1:
                raise ValueError("account_id not in database {0}".format(msg))


if __name__ == "__main__":
    couch = Account()
    couch.add_account("Couch", "Master")
    # couch = Account(1)
    # couch.add_account("", "")
    couch.delete_account()
