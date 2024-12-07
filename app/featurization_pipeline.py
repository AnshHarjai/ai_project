from pymongo import MongoClient
from bson.objectid import ObjectId
def fetch_raw_data():
    """Fetch raw data from MongoDB."""
    client = MongoClient('mongodb://mongodb:27017/')
    db = client["RAG_DB"]
    collection = db["raw_data"]
    raw_data = list(collection.find_one({"_id" : ObjectId("6752fdad321efdca8722a6d3")}))
    print(f"Fetched {len(raw_data)} documents from MongoDB.")
    print("Fetched raw data:", raw_data)
    return raw_data
from sentence_transformers import SentenceTransformer

def generate_embeddings(raw_data):
    """Convert text data into embeddings."""
    model = SentenceTransformer('all-MiniLM-L6-v2')  # Lightweight embedding model
    embeddings = []
    for doc in raw_data:
        if isinstance(doc, dict) and "content" in doc:  # Ensure doc is a dictionary with 'content' key
            embedding = model.encode(doc["content"])
            embeddings.append({"id": str(doc["_id"]), "embedding": embedding})
        else:
            print(f"Skipping invalid document: {doc}")  # Debugging output
    print(f"Generated embeddings for {len(embeddings)} documents.")
    return embeddings


from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance

def connect_qdrant():
    """Initialize connection to Qdrant."""
    client = QdrantClient(url="http://qdrant:6333")  # Service name
    client.recreate_collection(
        collection_name="rag_vectors",
        vector_size=384,  # Vector size of the embedding model
        distance=Distance.COSINE,
    )
    print("Connected to Qdrant and collection initialized.")
    return client

def run_featurization_pipeline():
    """Run the Featurization Pipeline."""
    # Step 1: Fetch raw data
    raw_data = fetch_raw_data()
    
    # Step 2: Generate embeddings
    embeddings = generate_embeddings(raw_data)
    
    # Step 3: Connect to Qdrant and store embeddings
    qdrant_client = connect_qdrant()
    store_embeddings_in_qdrant(qdrant_client, embeddings)

if __name__ == "__main__":
    run_featurization_pipeline()
