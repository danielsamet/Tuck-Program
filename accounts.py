from datetime import datetime
import sqlite3


class Account:
    """loads provided account details into the object with ability to run the functions below on the object accordingly
    """

    def __init__(self, account_id=None):
        """initialises account object with all attributes"""
        # f_name, l_name, account_id=None, balance=0, spending_limit=None, discount=None,
        #                  sub_zero_allowance=None, notes="", date_created=None, void=False
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
            raise ValueError("account cannot have an id to be inserted (new accounts will auto-generate ids)")

        self._db_execute("INSERT INTO accounts VALUES (NULL, ?, ?, ?, ?, ?, ?)",
                         (f_name, l_name, notes, 0, datetime.now(), 0))

        self.f_name, self.l_name, self.notes = f_name, l_name, notes

    def delete_account(self):
        """deletes account from database using account_id"""

        if self.account_id is None:
            raise ValueError("account not in database (thus it cannot be deleted)")
        # self._db_execute("DELETE FROM accounts WHERE account_ID = {0}".format(self.account_id))

        self.void = True
        self.update_account()

    def update_account(self):
        """updates account in database with any new data"""
        # note: cannot just run the delete and add functions as the database could have related records for the account,
        # e.g. discounts

        if self.account_id is None:
            raise ValueError("account not in database (thus it cannot be updated)")

        self._db_execute("UPDATE accounts SET first_name=\"{0}\", last_name=\"{1}\", notes=\"{2}\", void=\"{3}\" WHERE "
                         "account_id={4}".format(self.f_name, self.l_name, self.notes, self.void, self.account_id))

    def update_balance(self, amount):
        """updates balance in database"""

        self._db_execute("INSERT INTO accounts_top_ups VALUES (?, ?, ?)", (self.account_id, amount, datetime.now()))
        self.balance += amount
        self.update_account()

    def add_discount(self, amount, type_):
        """adds new discount to database for the account to be applied to all purchases by account"""

        self._db_execute("INSERT INTO accounts_discount VALUES (?, ?, ?, ?, ?, ?)", (self.account_id, amount, type_, ))

    def delete_discount(self):
        """deletes discount from database for the account"""

        pass

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


if __name__ == "__main__":
    # daniel = Account()
    # daniel.add_account("Couch", "Master")
    daniel = Account(1)
    # daniel.delete_account()
