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

    select += ", accounts.balance"

    select += ", n.notes"
    join += " LEFT JOIN "
    if notes:  # get all
        join += "accounts_notes"
    else:  # only get last
        join += "(SELECT MAX(date) mxdate, account_ID, notes from accounts_notes GROUP BY account_ID)"
    join += " as n ON accounts.account_ID=n.account_ID"

    count = int()
    for key, val in {"accounts.account_id": account_id, "f.name": f_name, "l.name": l_name,
                     "t.amount": top_ups, "n.notes": notes}.items():
        if val is not None:
            where = " AND " + where if count > 0 else where
            where += "{0}=\"{1}\"".format(key, val)
            count += 1

    where += "{0}accounts.void != 1".format(" AND " if where != " WHERE " else "")

    sql_command = select + " FROM accounts " + join + where

    return _db_execute(sql_command)


def get_products(product_id=None, name=None, supplier=None, notes=None):
    select = "SELECT products.product_ID"
    join = str()
    where = str()

    select += ", p.name"
    join += "INNER JOIN (SELECT MAX(date) mxdate, product_ID, name from products_name GROUP BY product_ID) " \
            "as p ON products.product_ID=p.product_ID"

    select += ", s.name"
    join += " LEFT JOIN (SELECT MAX(date) mxdate, product_ID, name from products_supplier GROUP BY product_ID)" \
            " as s ON products.product_ID=s.product_ID"

    select += ", c.price"
    join += " LEFT JOIN (SELECT MAX(date) mxdate, product_ID, price from products_cost_price GROUP BY product_ID)" \
            " as c ON products.product_ID=c.product_ID"

    select += ", s_.price"
    join += " LEFT JOIN (SELECT MAX(date) mxdate, product_ID, price from products_sale_price GROUP BY product_ID)" \
            " as s_ ON products.product_ID=s_.product_ID"

    select += ", products.quantity"

    select += ", n.notes"
    join += " LEFT JOIN "
    if notes:  # get all
        join += "products_notes"
    else:  # only get last
        join += "(SELECT MAX(date) mxdate, product_ID, notes from products_notes GROUP BY product_ID)"
    join += " as n ON products.product_ID=n.product_ID"

    count = int()
    for key, val in {"products.product_id": product_id, "p.name": name, "s.name": supplier,
                     "n.notes": notes}.items():
        if val is not None:
            where = where + " AND " if count > 0 else " WHERE "
            where += "{0}=\"{1}\"".format(key, val)
            count += 1

    where += " WHERE products.void != 1"

    sql_command = select + " FROM products " + join + where

    # sql_command = "SELECT * FROM products WHERE void != 1"

    return _db_execute(sql_command)


def get_item_history(table_name, item_id_name, item_id):
    return _db_execute("SELECT * FROM {0} WHERE {1}={2}".format(table_name, item_id_name, item_id))


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
        where += " WHERE account_id={0} AND void=0 and " \
                 "(datetime(\"now\") BETWEEN datetime(start_date) AND datetime(end_date) OR" \
                 " (datetime(\"now\") > date(start_date) AND end_date = \"\"))".format(account_id)

    return _db_execute(select + where)


def get_product_conditions(product_id=None, discount=False, purchase_limit=False, offer=False):
    select = "SELECT * "
    where = str()

    if discount:
        select += "FROM products_discounts"
    elif purchase_limit:
        select += "FROM products_purchase_limit"
    elif offer:
        select += "FROM products_offers"
    else:
        raise ValueError("Exactly one of the following must be set to True: discount, spending_limit or "
                         "sub_zero_allowance")

    if product_id is not None:
        where += " WHERE product_id={0} AND void=0 AND " \
                 "(datetime(\"now\") BETWEEN datetime(start_date) AND datetime(end_date) OR" \
                 " (datetime(\"now\") > date(start_date) AND end_date = \"\"))".format(product_id)

    return _db_execute(select + where)


def insert_new(table_name, fields):
    """inserts new records using the iterable parameter fields containing the field values in order"""
    _db_execute("INSERT INTO {0} VALUES ({1})".format(table_name, ", ".join(["?"]*len(fields))), fields)


def update(table_name, fields, primary_key):
    """updates a given table with fields and primary_key where fields is an iterable of tuples containing field name and
    value and primary_key is a tuple of type of primary key name and value"""

    sql_command = "UPDATE {0} SET {1} WHERE {2}".format(table_name, " AND ".join(["\"{0}\"=\"{1}\"".format(
        field[0], field[1]) for field in fields]), "\"{0}\"=\"{1}\"".format(primary_key[0], primary_key[1]))
    _db_execute(sql_command)


def get_transactions():
    pass


if __name__ == '__main__':
    # print(get_accounts())
    # print(get_account_conditions(account_id=6, discount=True))
    # from datetime import datetime
    # insert_new("accounts_l_name", [1, "Daniel", datetime.now()])
    # update("accounts_l_name", [("name", "Only Couch")], ("date", '2018-07-08 18:50:47.594578'))
    print(get_product_conditions(product_id=1, discount=True))
    print(_db_execute("SELECT * FROM products_purchase_limit "
                      "WHERE product_id = 4 AND void=0 AND "
                      "datetime(\"now\") BETWEEN datetime(start_date) AND datetime(end_date) OR "
                      "(datetime(\"now\") > date(start_date) AND end_date = \"\")"))

    # print(_db_execute("SELECT datetime(\"start_date\") FROM products_purchase_limit"))
