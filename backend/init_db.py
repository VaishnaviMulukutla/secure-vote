# backend/init_db.py

import sqlite3
import os

# Base directory of this script (backend/)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Database file path (e.g., backend/voters.db)
DB_PATH = os.path.join(BASE_DIR, 'voters.db')

# Name of the folder containing registered voter photos (e.g., backend/stored_photos/)
PHOTO_FOLDER_NAME = "stored_photos"
# Full path to the photo folder
PHOTO_FOLDER_FULL_PATH = os.path.join(BASE_DIR, PHOTO_FOLDER_NAME)


# List of (voter_id, photo_filename)
# Ensure these photo files (e.g., V0001.jpg) exist in your PHOTO_FOLDER_FULL_PATH
VOTERS_DATA = [
    ("v0001", "v0001.jpg"),
    ("v0002", "v0002.jpg"),
    ("v0003", "v0003.jpg"),
    ("v0004", "v0004.jpg"),
    ("v0005", "v0005.jpg"),
    ("v0006", "v0006.jpg"),
    ("v0007", "v0007.jpg"),
    ("v0008", "v0008.jpg"),
    ("v0009", "v0009.jpg"),
    ("v0010", "v0010.jpg"), # New additions start here
    ("v0011", "v0011.jpg"),
    ("v0012", "v0012.jpg"),
    ("v0013", "v0013.jpg"),
    ("v0014", "v0014.jpg"),
    ("v0015", "v0015.jpg"),
    ("v0016", "v0016.jpg"),
    ("v0017", "v0017.jpg"),
    ("v0018", "v0018.jpg"),
    ("v0019", "v0019.jpg"),
    ("v0020", "v0020.jpg"),
    ("v0021", "v0021.jpg"),
]

def init_db():
    # Ensure the stored_photos directory exists, or at least warn if not.
    if not os.path.isdir(PHOTO_FOLDER_FULL_PATH):
        print(f"‼️ Error: Photo folder '{PHOTO_FOLDER_FULL_PATH}' not found. Please create it and add voter images.")
        # You might want to create it: os.makedirs(PHOTO_FOLDER_FULL_PATH, exist_ok=True)
        # For now, we'll proceed but photo existence checks will fail.

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create voters table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS voters (
            voter_id TEXT PRIMARY KEY,
            photo_path TEXT NOT NULL,
            has_voted INTEGER DEFAULT 0
        )
    ''')
    print("📄 Table 'voters' ensured to exist.")

    # Populate with voter data
    added_count = 0
    for voter_id, photo_filename in VOTERS_DATA:
        # This is the path that will be stored in the DB, relative to the backend directory
        # e.g., "stored_photos/V0001.jpg"
        db_photo_path = os.path.join(PHOTO_FOLDER_NAME, photo_filename)

        # This is the actual path on the filesystem to check if the photo exists
        actual_photo_file_path = os.path.join(PHOTO_FOLDER_FULL_PATH, photo_filename)

        if not os.path.exists(actual_photo_file_path):
            print(f"⚠️ Warning: Photo not found for {voter_id} at '{actual_photo_file_path}'. Skipping this voter.")
            continue

        try:
            cursor.execute('''
                INSERT OR IGNORE INTO voters (voter_id, photo_path, has_voted) VALUES (?, ?, 0)
            ''', (voter_id, db_photo_path))
            if cursor.rowcount > 0:
                added_count +=1
                print(f"➕ Added voter: {voter_id} with photo {db_photo_path}")
            # else:
            #    print(f"ℹ️ Voter {voter_id} already exists. Skipping.")

        except sqlite3.Error as e:
            print(f"❌ SQLite error for {voter_id}: {e}")


    conn.commit()
    conn.close()

    if added_count > 0:
        print(f"✅ Database initialized/updated with {added_count} new voters.")
    else:
        print("ℹ️ No new voters added. Database may already be up to date.")

if __name__ == "__main__":
    print("🚀 Initializing database...")
    init_db()
    print("🎉 Database initialization process complete.")