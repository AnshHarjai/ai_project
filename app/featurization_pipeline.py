import logging
import spacy
from pymongo import MongoClient
from qdrant_client import QdrantClient, models
from qdrant_client.models import VectorParams, Distance
from qdrant_client.http.exceptions import UnexpectedResponse

# Logging setup
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# Load SpaCy large model
nlp = spacy.load("en_core_web_lg")


# Step 1: Fetch raw data
def fetch_raw_data():
    """Fetch raw data from MongoDB."""
    try:
        client = MongoClient("mongodb://mongodb:27017/")
        db = client["RAG_DB"]
        collection = db["raw_data"]
        raw_data = list(collection.find())
        logging.info(f"Fetched {len(raw_data)} documents from MongoDB.")
        return raw_data
    except Exception as e:
        logging.error(f"Error fetching data from MongoDB: {e}")
        return []


def chunk_data(data, chunk_size=200):
    """Chunk data into smaller pieces by words."""
    words = data.split()
    chunks = []
    for i in range(0, len(words), chunk_size):
        chunks.append(" ".join(words[i:i + chunk_size]))
    return chunks


# Step 2: Generate embeddings
import uuid

def generate_embeddings(raw_data):
    """Generate embeddings using SpaCy's large model."""
    embeddings = []
    nlp = spacy.load("en_core_web_lg")

    for doc in raw_data:
        if "content" in doc:
            chunks = chunk_data(doc['content'])
            for chunk in chunks:
                doc_chunk = nlp(chunk)
                embedding = doc_chunk.vector
                payload = {
                    "source": doc.get("source", ""),
                    "url": doc.get("url", ""),
                    "file_name": doc.get("file_name", ""),
                    "repo_name": doc.get("repo_name", ""),
                    "content": chunks,
                    "chunk": chunk,
                }
                embeddings.append({
                    'id': str(uuid.uuid4()),
                    'embedding': embedding.tolist(),
                    'payload': payload
                })
        else:
            logging.warning(f"Skipping document without content: {doc}")

    logging.info(f"Generated embeddings for {len(embeddings)} documents.")
    return embeddings


# Step 3: Connect to Qdrant
def connect_qdrant():
    """Initialize connection to Qdrant."""
    try:
        client = QdrantClient(url="http://qdrant:6333")  # Use service name
        collection_name = "rag_vectors"

        # Manually check if the collection exists
        collections = client.get_collections().collections
        print(f"Collections fetched{collections}")
        if any(c.name == collection_name for c in collections):
            logging.info(f"Collection '{collection_name}' already exists.")
        else:
            client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=300,  # Vector size of the embedding model
                    distance=Distance.COSINE,  # Similarity metric
                )
            )
            logging.info(f"Collection '{collection_name}' created.")
        return client
    except Exception as e:
        logging.error(f"Error connecting to Qdrant: {e}")
        return None


# Step 4: Store embeddings in Qdrant
def store_embeddings_in_qdrant(client, embeddings):
    """Store embeddings in Qdrant."""
    try:
        points = [
            models.PointStruct(
                id=embedding["id"], vector=embedding["embedding"], payload=embedding.get("payload", {})
            ) 
            for embedding in embeddings
        ]
        
        client.upload_points(
            collection_name="rag_vectors",
            points=points,
        )
        
        logging.info(f"Stored {len(points)} embeddings in Qdrant.")
    except Exception as e:
        logging.error(f"Error storing embeddings in Qdrant: {e}")


def delete_qdrant_collection(collection_name):
    """Delete a collection in Qdrant."""
    try:
        client = QdrantClient(url="http://qdrant:6333")  # Use the appropriate URL for your Qdrant instance
        client.delete_collection(collection_name=collection_name)
        logging.info(f"Collection '{collection_name}' deleted successfully.")
    except Exception as e:
        logging.error(f"Error deleting collection '{collection_name}': {e}")


# Main Featurization Pipeline
def run_featurization_pipeline():
    """Run the Featurization Pipeline."""

    # Step 1: Fetch raw data from mongodb
    raw_data = fetch_raw_data()

    if not raw_data:
        logging.error("No raw data found. Exiting pipeline.")
        return

    # Step 2: Generate embeddings
    embeddings = generate_embeddings(raw_data)

    # Step 3: Connect to Qdrant and store embeddings
    qdrant_client = connect_qdrant()
    store_embeddings_in_qdrant(qdrant_client, embeddings)

# if __name__ == "__main__":
#     run_featurization_pipeline()
