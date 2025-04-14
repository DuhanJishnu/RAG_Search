import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from flask_cors import CORS
from langchain_mistralai import MistralAIEmbeddings
from langchain_community.vectorstores.upstash import UpstashVectorStore
from waitress import serve
from langchain_core.documents import Document

load_dotenv()
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
UPSTASH_VECTOR_REST_URL = os.getenv("UPSTASH_VECTOR_REST_URL")
UPSTASH_VECTOR_REST_TOKEN = os.getenv("UPSTASH_VECTOR_REST_TOKEN")

app = Flask(__name__)
CORS(app)

@app.route("/api/search/embed_store", methods=["POST"])
def embed():
    try:
        data = request.get_json()
        text = data["itemDesc"]
        
        embeddings = MistralAIEmbeddings(
            model="mistral-embed",
        )

        documents = [Document(page_content=text)]

        store = UpstashVectorStore(
            embedding=embeddings
        )

        store.add_documents(documents)

        return jsonify({"message": "Successfully inserted vectors"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/search/query", methods=["POST"])
def query():
    try:
        data = request.get_json()
        query_text = data["query"]

        embeddings = MistralAIEmbeddings(
            model="mistral-embed",
        )

        store = UpstashVectorStore(
            embedding=embeddings
        )

        results = store.similarity_search(query_text, k=10)

        # Convert Documents to serializable format
        serializable_results = [{"page_content": doc.page_content, "metadata": doc.metadata} for doc in results]

        return jsonify({"results": serializable_results}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    serve(app, host="0.0.0.0", port=4000)