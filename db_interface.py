import sqlite3


def _db_open(database_name, foreign_keys=True):
    """internal use only - opens connections to database"""

    connection = sqlite3.connect(database_name)
    cursor = connection.cursor()
    if foreign_keys:
        cursor.execute("PRAGMA foreign_keys = 1")

    return connection, cursor


def _db_execute(sql_command, *parameters):
    """internal use only - executes commands on database and returns results"""

    connection, cursor = _db_open("tuck.db")

    try:
        cursor.execute(sql_command, *parameters)
    except ValueError:
        raise ValueError("operation parameter must be str \n(sql_command={0}, \nparameters={1})".format(sql_command,
                                                                                                        parameters))
    connection.commit()
    results = cursor.fetchall()

    cursor.close(), connection.close()

    return results


def get_accounts(_all=True, f_name=False, l_name=False, top_ups=False, notes=False):
    select = "SELECT accounts.account_ID"
    join = str()
    where = ""

    if f_name or _all:
        select += ", f.name"
        join += "INNER JOIN (SELECT MAX(date) mxdate, account_ID, name from accounts_f_name GROUP BY account_ID) " \
                "as f ON accounts.account_ID=f.account_ID"

        # where += "WHERE f.date=(SELECT MAX(accounts_f_name.date) FROM accounts_f_name) "

    if l_name or _all:
        select += ", l.name"
        join += " INNER JOIN (SELECT MAX(date) mxdate, account_ID, name from accounts_l_name GROUP BY account_ID)" \
                " as l ON accounts.account_ID=l.account_ID"

    if top_ups or _all:
        select += ", t.amount"
        join += " INNER JOIN "
        if top_ups:  # get all
            join += "accounts_top_ups"
        else:  # only get last
            join += "(SELECT MAX(date) mxdate, account_ID, amount from accounts_top_ups GROUP BY account_ID)"
        join += "as t ON accounts.account_ID=t.account_ID"

    if notes or _all:
        select += ", n.notes"
        join += " INNER JOIN "
        if notes:  # get all
            join += "accounts_notes"
        else:  # only get last
            join += "(SELECT MAX(date) mxdate, account_ID, notes from accounts_notes GROUP BY account_ID)"
        join += "as n ON accounts.account_ID=n.account_ID"

    sql_command = select + " FROM accounts " + join + where
    return _db_execute(sql_command)


def get_products():
    pass


def get_conditions():
    pass


def get_transactions():
    pass
