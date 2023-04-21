import os
import sqlite3
import sys

sys.path.append(os.path.dirname(os.path.realpath("backend")))
sys.path.append(os.path.dirname(os.path.realpath("backend/state.py")))
from backend.paths import Path

if __name__ == '__main__':
    conn = None
    try:
        conn = sqlite3.connect(Path.assets_database)
        print("connected to database")
    except:
        print(f"error")

    cursor = conn.cursor()
    cursor.execute("SELECT * FROM unlockables")
    unlockables_rows = cursor.fetchall()

    cursor.execute("SELECT * FROM killers")
    killers_rows = cursor.fetchall()

    # killer addons - also need to manually modify for: skull merchant
    # for i, killer in enumerate(killers_rows, 1):
    #     cursor.execute("SELECT id, category FROM unlockables WHERE category == ? ORDER BY ROWID", [killer[0]])
    #     rows = cursor.fetchall()
    #     for j, row in enumerate(rows):
    #         cursor.execute("UPDATE unlockables SET \"order\" = ? WHERE id == ? AND category == ?",
    #                        [100000 + i * 100 + j, row[0], row[1]])

    # killer perks
    # cursor.execute("SELECT id, category FROM unlockables WHERE type == 'perk' AND category == 'killer' ORDER BY ROWID")
    # rows = cursor.fetchall()
    # for i, row in enumerate(rows):
    #     cursor.execute("UPDATE unlockables SET \"order\" = ? WHERE id == ? AND category == ?",
    #                    [500000 + i, row[0], row[1]])

    # survivor perks
    # cursor.execute("SELECT id, category FROM unlockables WHERE type == 'perk' AND category == 'survivor' ORDER BY ROWID")
    # rows = cursor.fetchall()
    # for i, row in enumerate(rows):
    #     cursor.execute("UPDATE unlockables SET \"order\" = ? WHERE id == ? AND category == ?",
    #                    [600000 + i, row[0], row[1]])

    conn.commit()
    conn.close()
    print("disconnected from database")