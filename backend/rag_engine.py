import os
import sqlite3
import logging  
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from transformers import pipeline
import warnings
from flask import Flask, request, jsonify
from flask_cors import CORS


warnings.filterwarnings("ignore")

# === Logging Setup ===
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, "rag_engine.log")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Constants
DB_PATH = "DB/face_data.db"
INDEX_PATH = "vector_store"
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
QA_MODEL = "google/flan-t5-base"

# Flask app setup
app = Flask(__name__)
CORS(app)

# Step 1: Connect to DB and extract user data
def extract_user_data():
    logging.info("Extracting user data from database.")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT id, name, timestamp FROM users")
    users = cursor.fetchall()
    docs = []

    for user_id, name, timestamp in users:
        cursor.execute("SELECT COUNT(*) FROM faces WHERE user_id = ?", (user_id,))
        face_count = cursor.fetchone()[0]
        content = f"Name: {name}\nRegistered at: {timestamp}\nNumber of face images: {face_count}"
        docs.append(Document(page_content=content))

    conn.close()
    logging.info(f"Extracted {len(docs)} user documents.")
    return docs

# Step 2: Create or load FAISS index
def get_faiss_index(docs):
    logging.info("Loading FAISS index.")
    embedding_model = HuggingFaceEmbeddings(model_name=EMBED_MODEL)

    if os.path.exists(f"{INDEX_PATH}/index.faiss"):
        logging.info("FAISS index found. Loading existing index.")
        return FAISS.load_local(INDEX_PATH, embedding_model, allow_dangerous_deserialization=True)
    else:
        logging.info("FAISS index not found. Creating new index.")
        index = FAISS.from_documents(docs, embedding_model)
        index.save_local(INDEX_PATH)
        return index

# Step 3: Answer query with RAG
def answer_question(query, index, top_k=3):
    logging.info(f"Performing similarity search for query: {query}")
    results = index.similarity_search(query, k=top_k)
    context = "\n".join([doc.page_content for doc in results])

    qa = pipeline("text2text-generation", model=QA_MODEL)
    prompt = f"""Based on the context below, count how many people are registered. Each person is described by a Name and Registration time.Context:{context}Question: {query}"""    
    logging.info("Generating answer using Flan-T5.")
    response = qa(prompt, max_new_tokens=100)[0]['generated_text']
    logging.info("Answer generated successfully.")
    return response.strip()

# Step 4: Define API endpoint
@app.route('/api/ask', methods=['POST'])
def ask_question():
    logging.info("Received POST request at /api/ask.")
    data = request.get_json()
    if not data or 'query' not in data:
        logging.warning("Query parameter missing in request.")
        return jsonify({'error': 'Query parameter is missing'}), 400

    query = data['query']
    logging.info(f"Query received: {query}")

    try:
        docs = extract_user_data()
        index = get_faiss_index(docs)
        response = answer_question(query, index)
        return jsonify({'answer': response})
    except Exception as e:
        logging.error(f"Error processing request: {e}", exc_info=True)
        return jsonify({'error': 'An internal error occurred'}), 500

# === MAIN ===
if __name__ == "__main__":
    logging.info("Starting Flask server on port 8765.")
    app.run(host='0.0.0.0', port=8765)
