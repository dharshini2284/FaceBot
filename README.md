# FaceBot

FaceBot is a facial recognition-based chatbot platform built with a Python backend and a React frontend. It enables user registration, recognition, and interactive chatting features using a simple and intuitive UI.

---

## Setup Instructions

### Backend Setup

1. Navigate to the `backend` directory:

   ```bash
   cd backend
   ```

2. Create a virtual environment and activate it:

   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # On Mac: source .venv/bin/activate
   ```

3. Install the required Python packages:

   ```bash
   pip install -r requirements.txt
   ```

4. Run the backend server:

   ```bash
   python rag_engine.py
   ```

### Node Server 

```bash
cd backend/node
npm install
node server.js
```

---

### Frontend Setup

1. Navigate to `frontend`:

   ```bash
   cd frontend
   ```

2. Install dependencies:

   ```bash
   npm install
   ```

3. Start the React development server:

   ```bash
   npm start
   ```

---

## Architecture Overview

This project features a modular architecture integrating a **React frontend**, a **Node.js backend**, and **Python modules** for face recognition and retrieval-augmented generation (RAG), all connected via HTTP APIs.

### Frontend (React)

* **RegisterWidget**: Sends a `POST` request to `/api/register` with user data.
* **RecognizeWidget**: Sends a `GET` request to `/api/recognize` to initiate facial recognition.
* **ChatWidget**: Sends a `POST` request to `/api/ask` to receive intelligent RAG responses, and displays the result.

### Backend (Node.js)

* Acts as the central API server, exposing the following endpoints:

  * `POST /api/register`: Spawns `register.py` to store user data.
  * `GET /api/recognize`: Spawns `recognize.py` to perform face recognition.
  * `POST /api/ask`: Forwards query input to `rag_engine.py`.
* Uses `child_process.spawn` to execute Python scripts and manage I/O.

### Python Modules

* **register.py**: Handles registration logic, writes data to the SQLite database.
* **recognize.py**: Handles recognition logic, reads data from the database.
* **rag\_engine.py**: Processes input queries and interacts with the database to generate RAG responses.

### Database (SQLite)

* Serves as the persistent storage layer.
* Shared across all Python modules.

  * `register.py` writes user data.
  * `recognize.py` reads recognition data.
  * `rag_engine.py` reads user and knowledge data for generating responses.

*Diagram explaining the data flow between the React frontend, Python backend, and face recognition module.*
![arch](https://github.com/user-attachments/assets/92dbdcfc-f599-461f-a065-ffb9de6ae781)


---

## Demo Video

Watch the demo and explanation on Loom:
[👉 Loom Video Demo](https://www.loom.com/share/1ab3dfcfdb774dbd9df30ff10518881a?sid=6f25ce4d-6c3a-4550-ad08-3777d23b69ad)

---

## Assumptions

* Since OPENAI's API is not available due to payment, I used google/flan-t5-base model for question answering.
* I used SQLite for simplicity and lightweight storage

---

## Logs & Monitoring

Logging is structured using Python’s `logging` library:

* Logs are stored in `logs/face`\*`registartion.log,logs/face_recognition.log,logs/rag`\*engine`.log`.
* Each module (`register.py`, `recognize.py`, `rag_engine.py`) includes logging for tracking user events and errors.

---

## Acknowledgement

This project is a part of a hackathon run by [https://katomaran.com](https://katomaran.com)
