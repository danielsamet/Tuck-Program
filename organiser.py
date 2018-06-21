import sqlite3
import time


class Organiser:
    """quick db functionality (mainly for testing purposes) before GUI is built"""

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

    def create_database(self):
        """initialises the database with all necessary tables with correct structure"""

        sql_command = list()
        sql_command.append(
            """
            
            CREATE TABLE accounts (
                account_ID INTEGER PRIMARY KEY,
                balance INTEGER NOT NULL,
                date_added DATE NOT NULL,
                void INTEGER(1) NOT NULL
            );
            
            """)
        sql_command.append(
            """
            
            CREATE TABLE accounts_f_name (
                account_ID INETEGER,
                name VARCHAR(20) NOT NULL,
                date DATE PRIMARY KEY,
                    FOREIGN KEY (account_ID) REFERENCES accounts(account_ID)
            );
            
            """)
        sql_command.append(
            """

            CREATE TABLE accounts_l_name (
                account_ID INTEGER,
                name VARCHAR(30) NOT NULL,
                date DATE PRIMARY KEY,
                    FOREIGN KEY (account_ID) REFERENCES accounts(account_ID)
            );

            """)
        sql_command.append(
            """
            
            CREATE TABLE accounts_top_ups (
                account_ID INTEGER,
                amount INTEGER NOT NULL,
                date DATE PRIMARY KEY,
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
                end_date DATE,
                void INTEGER(1) NOT NULL,
                date DATE PRIMARY KEY,
                    FOREIGN KEY (account_ID) REFERENCES accounts(account_ID)
            );
            
            """)
        sql_command.append(
            """
            
            CREATE TABLE accounts_spending_limit (
                account_ID INTEGER,
                amount INTEGER NOT NULL,
                per VARCHAR(10) NOT NULL,
                start_date DATE NOT NULL,
                end_date DATE,
                void INTEGER NOT NULL,
                date DATE PRIMARY KEY,
                    FOREIGN KEY (account_ID) REFERENCES accounts(account_ID)
            );
            
            """)
        sql_command.append(
            """
            
            CREATE TABLE accounts_sub_zero_allowance (
                account_ID INTEGER,
                amount INTEGER NOT NULL,
                start_date DATE NOT NULL,
                end_date DATE,
                void INTEGER NOT NULL,
                date DATE PRIMARY KEY,
                    FOREIGN KEY (account_ID) REFERENCES accounts(account_ID)
            );
            
            """)
        sql_command.append(
            """

            CREATE TABLE accounts_notes (
                account_ID INTEGER,
                notes VARCHAR(255),
                date DATE PRIMARY KEY,
                    FOREIGN KEY (account_ID) REFERENCES accounts(account_ID)
            );

            """)
        sql_command.append(
            """
            
            CREATE TABLE products (
                product_ID INTEGER PRIMARY KEY,
                quantity INTEGER,
                date_added DATE NOT NULL,
                void INTEGER NOT NULL
            );
            
            """)
        sql_command.append(
            """

            CREATE TABLE products_name (
                product_ID INTEGER,
                name VARCHAR(30) NOT NULL,
                date DATE PRIMARY KEY,
                    FOREIGN KEY (product_ID) REFERENCES products(product_ID)
            );

            """)
        sql_command.append(
            """

            CREATE TABLE products_supplier (
                product_ID INTEGER,
                name VARCHAR(30) NOT NULL,
                date DATE PRIMARY KEY,
                    FOREIGN KEY (product_ID) REFERENCES products(product_ID)
            );

            """)
        sql_command.append(
            """

            CREATE TABLE products_cost_price (
                product_ID INTEGER,
                price INTEGER NOT NULL,
                date DATE PRIMARY KEY,
                    FOREIGN KEY (product_ID) REFERENCES products(product_ID)
            );

            """)
        sql_command.append(
            """

            CREATE TABLE products_sale_price (
                product_ID INTEGER,
                price INTEGER NOT NULL,
                date DATE PRIMARY KEY,
                    FOREIGN KEY (product_ID) REFERENCES products(product_ID)
            );

            """)
        sql_command.append(
            """

            CREATE TABLE products_quantity_top_ups (
                product_ID INTEGER,
                amount INTEGER NOT NULL,
                date DATE PRIMARY KEY,
                    FOREIGN KEY (product_ID) REFERENCES products(product_ID)
            );

            """)
        sql_command.append(
            """
            
            CREATE TABLE products_discounts (
                product_ID INTEGER,
                amount INTEGER NOT NULL,
                type VARCHAR(1) NOT NULL,
                start_date DATE NOT NULL,
                end_date DATE,
                void INTEGER NOT NULL,
                date DATE PRIMARY KEY,
                    FOREIGN KEY (product_ID) REFERENCES products(product_ID)
            );
            
            """)
        sql_command.append(
            """

            CREATE TABLE products_purchase_limit (
                product_ID INTEGER,
                amount INTEGER NOT NULL,
                per VARCHAR(10) NOT NULL,
                start_date DATE NOT NULL,
                end_date DATE,
                void INTEGER NOT NULL,
                date DATE PRIMARY KEY,
                    FOREIGN KEY (product_ID) REFERENCES products(product_ID)
            );

            """)
        sql_command.append(
            """
            
            CREATE TABLE products_offers (
                product_ID INTEGER,
                buy_x INTEGER NOT NULL,
                get_y INTEGER NOT NULL,
                z_off INTEGER NOT NULL,
                type INTEGER(1) NOT NULL,
                start_date DATE NOT NULL,
                end_date DATE,
                void INTEGER NOT NULL,
                date DATE PRIMARY KEY,
                    FOREIGN KEY (product_ID) REFERENCES products(product_ID)
            );
            
            """)
        sql_command.append(
            """

            CREATE TABLE products_notes (
                product_ID INTEGER,
                notes VARCHAR(255),
                date DATE PRIMARY KEY,
                    FOREIGN KEY (product_ID) REFERENCES products(product_ID)
            );

            """)
        sql_command.append(
            """

            CREATE TABLE transactions (
                transaction_ID INTEGER PRIMARY KEY,
                account_ID INTEGER NOT NULL,
                amount INTEGER NOT NULL,
                date DATE NOT NULL,
                void INTEGER NOT NULL,
                    FOREIGN KEY (account_ID) REFERENCES accounts(account_ID)
            );

            """)
        sql_command.append(
            """

            CREATE TABLE transactions_products (
                transaction_ID INTEGER,
                product_ID INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                    PRIMARY KEY (transaction_ID, product_ID, quantity),
                    FOREIGN KEY (transaction_ID) REFERENCES transactions(transaction_ID),
                    FOREIGN KEY (product_ID) REFERENCES products(product_ID)
            );

            """)

        for command in sql_command:
            try:
                self._db_execute(command)
            except sqlite3.OperationalError:  # tables already exist (no need to worry abt one existing and not another)
                print("table already exists\n")

    def show_database_structure(self):
        """returns current database structure"""

        tables = [item[0] for item in self._db_execute("SELECT name FROM sqlite_master WHERE type='table';")]

        for table in tables:
            print("Showing table structure for table \"{0}\":".format(table))
            [print("\t", column) for column in self._db_execute("PRAGMA TABLE_INFO({})".format(table))]

        print("")

    def show_table(self, table_name):
        """returns table of data (using table_name)"""

        print("Records found in table \"{0}\":".format(table_name))

        table = self._db_execute("SELECT * FROM {}".format(table_name))

        [print(table) for table in table]
        if not table:
            print("--No Records in Table--")
        print("")

    def show_all_tables(self):
        """returns records for all tables"""

        tables = [item[0] for item in self._db_execute("SELECT name FROM sqlite_master WHERE type='table';")]
        [self.show_table(table) for table in tables]

    def purge_data(self):
        """purge database of all data leaving just table structure"""

        tables = [item[0] for item in self._db_execute("SELECT name FROM sqlite_master WHERE type='table';")]

        deleted = int()
        while deleted < len(tables):
            for table in tables:
                try:
                    try:
                        self._db_execute("DROP TABLE {}".format(table))
                        deleted += 1
                    except sqlite3.OperationalError:  # table has already been dropped
                        continue
                except sqlite3.IntegrityError:  # there are related records which must be deleted first
                    time.sleep(0.01)

        self.create_database()


if __name__ == "__main__":
    # Organiser().create_database()
    Organiser().show_database_structure()
    Organiser().show_all_tables()
    Organiser().purge_data()
