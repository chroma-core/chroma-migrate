import numpy as np
import random

import chromadb
from chromadb.api import API
from chromadb.config import Settings

# Run this to populate a test clickhouse database
def gen():    
    # Create a new API
    api: API = chromadb.Client(Settings(chroma_api_impl="rest", chroma_server_host="localhost", chroma_server_http_port="8000"))

    # Create a random set of collections
    for i in range(10):
        collection = api.get_or_create_collection(f"collection_{i}")
        # Add a random set of embeddings
        N = random.randint(1, 100)
        D = random.randint(10, 100)
        embeddings = np.random.rand(N, D).tolist()
        metadata = [{f"{i}": f"{i}"} for i in range(N)]
        documents = [f"document_{i}" for i in range(N)]
        ids = [f"id_{i}" for i in range(N)]
        collection.add(ids, embeddings, metadata, documents)
        print(f"Added {N} embeddings to collection {collection.name}")
    
if __name__ == "__main__":
    gen()