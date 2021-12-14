import sqlite3

from paths import Path

class Unlockable:
    def __init__(self, unlockable_id, name, category, rarity, notes):
        self.id = unlockable_id
        self.name = name
        self.category = category
        self.rarity = rarity
        self.notes = notes

class Data:
    @staticmethod
    def __connection():
        connection = None
        try:
            connection = sqlite3.connect(Path.assets_database)
            print("connected to database")
        except:
            print(f"error")
        return connection

    @staticmethod
    def get_unlockables():
        connection = Data.__connection()

        cursor = connection.cursor()
        cursor.execute("SELECT * FROM unlockables")
        rows = cursor.fetchall()

        unlockables = [Unlockable(*row) for row in rows]
        connection.close()
        return unlockables

    @staticmethod
    def get_killers():
        connection = Data.__connection()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM killers")
        rows = cursor.fetchall()

        killers = [killer for killer, in rows]
        connection.close()
        return killers


    @staticmethod
    def categories_as_tuples(categories=None):
        return [(u.category, u.id) for u in Data.get_unlockables()
                if categories is None or u.category in categories]