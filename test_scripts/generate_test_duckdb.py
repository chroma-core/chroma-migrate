import numpy as np
import random

import chromadb
from chromadb.api import API
from chromadb.config import Settings

# Run this to generate a test duckdb database
def gen():
    persist_directory_a = "./test_data_duckdb"
    
    # Create a new API
    api: API = chromadb.Client(Settings(chroma_db_impl="duckdb+parquet", persist_directory=persist_directory_a))

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
    
    api.persist()

if __name__ == "__main__":
    gen()