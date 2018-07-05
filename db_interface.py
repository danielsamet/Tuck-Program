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


def get_accounts(account_id=None, f_name=None, l_name=None, top_ups=None, notes=None):
    select = "SELECT accounts.account_ID"
    join = str()
    where = " WHERE "

    select += ", f.name"
    join += "INNER JOIN (SELECT MAX(date) mxdate, account_ID, name from accounts_f_name GROUP BY account_ID) " \
            "as f ON accounts.account_ID=f.account_ID"

    select += ", l.name"
    join += " INNER JOIN (SELECT MAX(date) mxdate, account_ID, name from accounts_l_name GROUP BY account_ID)" \
            " as l ON accounts.account_ID=l.account_ID"

    select += ", t.amount"
    join += " INNER JOIN "
    if top_ups:  # get all
        join += "accounts_top_ups"
    else:  # only get last
        join += "(SELECT MAX(date) mxdate, account_ID, amount from accounts_top_ups GROUP BY account_ID)"
    join += "as t ON accounts.account_ID=t.account_ID"

    select += ", n.notes"
    join += " INNER JOIN "
    if notes:  # get all
        join += "accounts_notes"
    else:  # only get last
        join += "(SELECT MAX(date) mxdate, account_ID, notes from accounts_notes GROUP BY account_ID)"
    join += "as n ON accounts.account_ID=n.account_ID"

    count = int()
    for key, val in {"accounts.account_id": account_id, "f.name": f_name, "l.name": l_name,
                     "t.amount": top_ups, "n.notes": notes}.items():
        if val is not None:
            where = where + " AND " if count > 0 else where
            where += "{0}=\"{1}\"".format(key, val)
            count += 1

    sql_command = select + " FROM accounts " + join + where
    return _db_execute(sql_command)


def get_products():
    pass


def get_account_conditions(account_id=None, discount=False, spending_limit=False, sub_zero_allowance=False):
    select = "SELECT * "
    where = str()

    if discount:
        select += "FROM accounts_discounts"
    elif spending_limit:
        select += "FROM accounts_spending_limit"
    elif sub_zero_allowance:
        select += "FROM accounts_sub_zero_allowance"
    else:
        raise ValueError("One of the following must be set to True: discount, spending_limit or sub_zero_allowance")

    if account_id is not None:
        where += " WHERE account_id={0}".format(account_id)

    return _db_execute(select + where)


def get_product_conditions(product_id=None, discount=False, purchase_limit=False, offer=False):
    select = "SELECT * "
    where = str()

    if discount:
        select += "FROM products_discounts"
    elif purchase_limit:
        select += "FROM prodcuts_purchase_limit"
    elif offer:
        select += "FROM products_offers"
    else:
        raise ValueError("One of the following must be set to True: discount, spending_limit or sub_zero_allowance")

    if product_id is not None:
        where += " WHERE product_id={0}".format(product_id)

    return _db_execute(select + where)


def get_transactions():
    pass


if __name__ == '__main__':
    print(get_accounts(f_name="Couch"))
    print(get_account_conditions(account_id=6, spending_limit=True))
