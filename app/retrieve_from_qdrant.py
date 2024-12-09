import logging
import spacy
from pymongo import MongoClient
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance
from qdrant_client.http.exceptions import UnexpectedResponse

# Logging setup
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# Load SpaCy large model
nlp = spacy.load("en_core_web_lg")

# Step 1: Convert a text query to embeddings
def text_to_embedding(text):
    """Convert text to embeddings using SpaCy."""
    doc = nlp(text)
    return doc.vector


# Step 2: Connect to Qdrant
def connect_qdrant():
    """Initialize connection to Qdrant."""
    try:
        client = QdrantClient(url="http://qdrant:6333")  # Use service name
        collection_name = "rag_vectors"
        return client
    except Exception as e:
        logging.error(f"Error connecting to Qdrant: {e}")
        return None

# Step 3: Retrieve the k most similar embeddings from the vector DB along with their score
def retrieve_similar_embeddings(client, query_embedding, k=5):
    """Retrieve the k most similar embeddings from Qdrant."""
    try:

        search_results = client.search(
            collection_name="rag_vectors",
            query_vector=query_embedding,
            limit=k
        )
        context = []
        for result in search_results:
            temp_dict = {
                'score': result.score,
                'chunk': result.payload['chunk']
            }
            context.append(temp_dict)
        return context
    
    except UnexpectedResponse as e:
        logging.error(f"Failed to retrieve embeddings from Qdrant: {e}")
        return []



def run_retrieve_pipeline(query_text):
    query_embedding = text_to_embedding(query_text)
    client = connect_qdrant()
    if client:
        search_results = retrieve_similar_embeddings(client, query_embedding, 5)
        return search_results
    else:
        return []


# if __name__ == "__main__":
#     query_text = "What is ROS2?"
#     query_embedding = text_to_embedding(query_text)
#     client = connect_qdrant()
#     if client:
#         search_results = retrieve_similar_embeddings(client, query_embedding, 5)
#         print(search_results)