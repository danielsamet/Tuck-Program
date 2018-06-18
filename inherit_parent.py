import sqlite3


class Inherit:
    """this class is designed purely for code sharing amongst different classes to reduce code duplication - not
    intended to be instantiated by itself"""

    def _db_open(self, database_name, foreign_keys=True):
        """internal use only - opens connections to database"""

        connection = sqlite3.connect(database_name)
        cursor = connection.cursor()
        if foreign_keys:
            cursor.execute("PRAGMA foreign_keys = 1")
        return connection, cursor

    def _db_execute(self, sql_command, *parameters):
        """internal use only - executes commands on database and returns results"""

        connection, cursor = self._db_open("tuck.db")

        try:
            cursor.execute(sql_command, *parameters)
        except ValueError:
            raise ValueError("operation parameter must be str \n(sql_command={0}, \nparameters={1})".format(sql_command,
                                                                                                            parameters))
        connection.commit()
        results = cursor.fetchall()

        cursor.close(), connection.close()

        return results
