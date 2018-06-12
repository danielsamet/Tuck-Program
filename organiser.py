class Organiser:
    """quick functionality (mainly for testing purposes) before GUI is built"""

    def create_database(self):
        """initialises the database with all necessary tables with correct structure"""

        pass

    def show_database_structure(self):
        """returns current database structure"""

        pass

    def show_table(self, table_name):
        """returns table of data (using table_name)"""

        pass

    def purge_data(self):
        """purge database of all data leaving just table structure"""

        pass


if __name__ is "__main__":
    Organiser().create_database()
    # Organiser().show_database_structure()
    # Organiser().show_table()
    # Organiser().purge_data()
