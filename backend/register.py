import cv2
import sqlite3
import numpy as np
import sys
import time
import logging
import os

# Setup logging
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, "face_registration.log")
logging.basicConfig(filename=log_file, level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")

# Check for name argument
if len(sys.argv) < 2:
    logging.error("Name not provided as a command-line argument.")
    print("Error: Name is required as an argument.")
    sys.exit(1)

name = sys.argv[1]
logging.info(f"Starting face registration for: {name}")
print(f"Registering face for {name}...")

# DB setup
try:
    conn = sqlite3.connect("DB/face_data.db")
    cursor = conn.cursor()
    logging.info("Database connection established.")
except Exception as e:
    logging.error(f"Failed to connect to database: {e}")
    sys.exit(1)

# Create tables if they don't exist
cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        timestamp TEXT NOT NULL
    )
""")
cursor.execute("""
    CREATE TABLE IF NOT EXISTS faces (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        image BLOB NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
""")
conn.commit()
logging.info("Tables ensured in database.")

# Face detection setup
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
cap = cv2.VideoCapture(0)

# User check and registration
cursor.execute("SELECT id FROM users WHERE name = ?", (name,))
user = cursor.fetchone()

if user is None:
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO users (name, timestamp) VALUES (?, ?)", (name, timestamp))
    conn.commit()
    user_id = cursor.lastrowid
    logging.info(f"New user {name} registered with ID {user_id} at {timestamp}.")
    print(f"New user {name} registered with timestamp {timestamp}.")
else:
    user_id = user[0]
    logging.info(f"Existing user {name} found with ID {user_id}.")
    print(f"User {name} found in the database.")

# Capture faces
saved_count = 0
max_images = 30
print("Capturing faces...")
logging.info("Started capturing faces.")

while True:
    ret, frame = cap.read()
    if not ret:
        logging.warning("Failed to capture frame from webcam.")
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    for (x, y, w, h) in faces:
        face = gray[y:y+h, x:x+w]
        face_resized = cv2.resize(face, (200, 200))
        _, buffer = cv2.imencode(".jpg", face_resized)
        image_blob = buffer.tobytes()

        cursor.execute("INSERT INTO faces (user_id, image) VALUES (?, ?)", (user_id, image_blob))
        conn.commit()
        saved_count += 1
        logging.info(f"Saved image {saved_count} for user ID {user_id}.")

        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        if saved_count >= max_images:
            break

    cv2.imshow("Register Face", frame)
    if cv2.waitKey(1) & 0xFF == ord('q') or saved_count >= max_images:
        logging.info("Face capture session ended by user or limit reached.")
        break

cap.release()
cv2.destroyAllWindows()
conn.close()
print(f"Saved {saved_count} face images to database.")
logging.info(f"Finished registration. Total images saved: {saved_count}.")
