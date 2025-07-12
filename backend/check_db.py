# backend/check_db.py (Corrected version)
import sqlite3

conn = sqlite3.connect("voters.db")
cursor = conn.cursor()

cursor.execute("SELECT voter_id, photo_path, has_voted FROM voters")
rows = cursor.fetchall()

if not rows:
    print("No voters found in the database.")
else:
    for row in rows:
        print(f"Voter ID: {row[0]}, Photo Path: {row[1]}, Has Voted: {bool(row[2])}")

conn.close()