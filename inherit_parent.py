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

    def _check_item_exists(self, cmd):
        """internal use only - checks item exists in database"""

        if len(self._db_execute(cmd)) == 0:
            return False

        return True

    def _get_last_id(self, table):
        """internal use only - returns the last id used in database"""

        column_name = self._db_execute("PRAGMA TABLE_INFO({0})".format(table))[0][1]
        ids = self._db_execute("SELECT {0} FROM {1}".format(column_name, table))

        return ids[-1][0]
