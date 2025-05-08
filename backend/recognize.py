import cv2
import sqlite3
import numpy as np
import os
import logging

# === Logging Setup ===
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, "face_recognition.log")
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# === Ensure Database Exists and Create Tables if Not ===
DB_PATH = "DB/face_data.db"

def create_db_if_not_exists():
    if not os.path.exists(DB_PATH):
        logging.info("Database not found. Creating new database and tables.")
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Create users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                timestamp TEXT NOT NULL
            )
        """)

        # Create faces table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS faces (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                image BLOB NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        conn.commit()
        conn.close()
        logging.info("Database and tables created successfully.")
    else:
        logging.info("Database already exists.")

# Create the database if not exists
create_db_if_not_exists()

# Load recognizer
recognizer = cv2.face.LBPHFaceRecognizer_create()

# Load data from DB
logging.info("Connecting to the database to fetch user data.")
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Fetch all user names from the users table
cursor.execute("SELECT id, name FROM users")
users = cursor.fetchall()

# Create a map for user names and labels
user_id_map = {user[1]: user[0] for user in users}

# Load face images and labels
faces = []
labels = []
label_map = {}
next_label = 0

# Fetch all face images and corresponding user_ids from the faces table
cursor.execute("SELECT user_id, image FROM faces")
rows = cursor.fetchall()

logging.info(f"Loaded {len(rows)} face records from the database.")

for row in rows:
    user_id, image_blob = row
    img_array = np.frombuffer(image_blob, np.uint8)
    img = cv2.imdecode(img_array, cv2.IMREAD_GRAYSCALE)

    # Ensure the name is properly mapped to the correct label
    name = None
    for user_name, db_user_id in user_id_map.items():
        if user_id == db_user_id:
            name = user_name
            break

    if name not in label_map:
        label_map[name] = next_label
        next_label += 1

    faces.append(img)
    labels.append(label_map[name])

conn.close()

# Train the face recognizer
logging.info("Training the face recognizer with loaded face data.")
recognizer.train(faces, np.array(labels))

# Reverse the label map to map labels back to names
label_map_rev = {v: k for k, v in label_map.items()}

# Start webcam for face recognition
logging.info("Starting webcam for face recognition.")
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    logging.error("Error: Could not open webcam.")
    exit()

logging.info("Webcam successfully opened, starting face recognition.")

while True:
    ret, frame = cap.read()
    if not ret:
        logging.warning("Failed to capture image from webcam.")
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces_detected = face_cascade.detectMultiScale(gray, 1.3, 5)

    for (x, y, w, h) in faces_detected:
        face = gray[y:y+h, x:x+w]
        face_resized = cv2.resize(face, (200, 200))

        # Predict the face label
        label, confidence = recognizer.predict(face_resized)

        # Retrieve the corresponding name using the label
        name = label_map_rev.get(label, "Unknown")

        # Display the name on the frame
        display_text = f"{name}"
        color = (0, 255, 0) if confidence < 100 else (0, 0, 255)

        # Draw a rectangle around the face
        cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)

        # Display the name above the face
        cv2.putText(frame, display_text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)

    cv2.imshow("Recognize Face", frame)

    # Break if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        logging.info("User pressed 'q' to quit face recognition.")
        break

# Release webcam and close windows
cap.release()
cv2.destroyAllWindows()

logging.info("Face recognition session ended.")
