import sqlite3


class Organiser:
    """quick db functionality (mainly for testing purposes) before GUI is built"""

    def db_opener(self, database_name, foreign_keys=True):
        connection = sqlite3.connect(database_name)
        cursor = connection.cursor()
        if foreign_keys:
            cursor.execute("PRAGMA foreign_keys = 1")
        return connection, cursor

    def create_database(self):
        """initialises the database with all necessary tables with correct structure"""

        sql_command = list()
        sql_command.append(
            """
            
            CREATE TABLE accounts (
                account_ID INTEGER PRIMARY KEY,
                first_name VARCHAR(20) NOT NULL,
                last_name VARCHAR(30) NOT NULL,
                balance INTEGER NOT NULL,
                notes VARCHAR(255),
                date_added DATE NOT NULL,
                void INTEGER(1) NOT NULL
            );
            
            """)
        sql_command.append(
            """
            
            CREATE TABLE accounts_top_ups (
                account_ID INTEGER,
                amount INTEGER NOT NULL,
                date_topped_up DATE NOT NULL,
                    FOREIGN KEY (account_ID) REFERENCES accounts(account_ID)
            );
            
            """
        )
        sql_command.append(
            """
            
            CREATE TABLE accounts_discounts (
                account_ID INTEGER,
                amount INTEGER NOT NULL,
                type INTEGER(1) NOT NULL,
                start_date DATE NOT NULL,
                end_date DATE NOT NULL,
                void INTEGER(1) NOT NULL,
                    FOREIGN KEY (account_ID) REFERENCES accounts(account_ID),
                    PRIMARY KEY (account_ID, amount, start_date, end_date)
            );
            
            """)
        sql_command.append(
            """
            
            CREATE TABLE accounts_spending_limit (
                account_ID INTEGER,
                amount INTEGER NOT NULL,
                start_date DATE NOT NULL,
                end_date DATE NOT NULL,
                void INTEGER NOT NULL,
                    FOREIGN KEY (account_ID) REFERENCES accounts(account_ID)
            );
            
            """)
        sql_command.append(
            """
            
            CREATE TABLE accounts_sub_zero_allowance (
                account_ID INTEGER,
                amount INTEGER NOT NULL,
                start_date DATE NOT NULL,
                end_date DATE NOT NULL,
                void INTEGER NOT NULL,
                    FOREIGN KEY (account_ID) REFERENCES accounts(account_ID)
            );
            
            """)
        sql_command.append(
            """
            
            CREATE TABLE transactions (
                transaction_ID INTEGER PRIMARY KEY,
                account_ID INTEGER NOT NULL,
                product_ID INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                date DATE NOT NULL,
                void INTEGER NOT NULL,
                    FOREIGN KEY (account_ID) REFERENCES accounts(account_ID),
                    FOREIGN KEY (product_ID) REFERENCES accounts(product_ID)
            );
            
            """)
        sql_command.append(
            """
            
            CREATE TABLE products (
                product_ID INTEGER PRIMARY KEY,
                product_name VARCHAR(30) NOT NULL,
                supplier VARCHAR(30) NOT NULL,
                cost_price INTEGER,
                selling_price INTEGER NOT NULL,
                quantity INTEGER,
                notes VARCHAR(255),
                date_added DATE NOT NULL,
                void INTEGER NOT NULL
            );
            
            """)
        sql_command.append(
            """
            
            CREATE TABLE products_purchase_limit (
                product_ID INTEGER,
                amount INTEGER NOT NULL,
                start_date DATE NOT NULL,
                end_date DATE NOT NULL,
                void INTEGER NOT NULL,
                    FOREIGN KEY (product_ID) REFERENCES accounts(product_ID)
            );
            
            """)
        sql_command.append(
            """
            
            CREATE TABLE products_discount (
                product_ID INTEGER,
                amount INTEGER NOT NULL,
                type VARCHAR(1) NOT NULL,
                start_date DATE NOT NULL,
                end_date DATE NOT NULL,
                void INTEGER NOT NULL,
                    FOREIGN KEY (product_ID) REFERENCES accounts(product_ID)
            );
            
            """)
        sql_command.append(
            """
            
            CREATE TABLE products_offers (
                product_ID INTEGER,
                buy_x INTEGER NOT NULL,
                get_y INTEGER NOT NULL,
                z_off INTEGER NOT NULL,
                start_date DATE NOT NULL,
                end_date DATE NOT NULL,
                void INTEGER NOT NULL,
                    FOREIGN KEY (product_ID) REFERENCES accounts(product_ID)
            );
            
            """)

        connection, cursor = self.db_opener("tuck.db", )

        try:
            for command in sql_command:
                cursor.execute(command)
            connection.commit()
        except sqlite3.OperationalError:  # tables already exist (no need to worry abt one existing and not another)
            print("table already exists")

        cursor.close(), connection.close()

    def show_database_structure(self):
        """returns current database structure"""

        connection, cursor = self.db_opener("tuck.db")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [item[0] for item in cursor.fetchall()]
        
        for table in tables:
            print(table)
            cursor.execute("PRAGMA TABLE_INFO({})".format(table))
            [print("\t", column) for column in cursor.fetchall()]
            
        cursor.close(), connection.close()

    def show_table(self, table_name):
        """returns table of data (using table_name)"""

        connection, cursor = self.db_opener("tuck.db")

        cursor.execute("SELECT * FROM {}".format(table_name))
        print(cursor.fetchall())

        cursor.close(), connection.close()

    def purge_data(self):
        """purge database of all data leaving just table structure"""

        connection, cursor = self.db_opener("tuck.db")

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [item[0] for item in cursor.fetchall()]
        [cursor.execute("DROP TABLE {}".format(table)) for table in tables]
        connection.commit()

        cursor.close(), connection.close()

        self.create_database()


if __name__ == "__main__":
    Organiser().create_database()
    # Organiser().show_database_structure()
    Organiser().show_table("accounts")
    # Organiser().purge_data()
