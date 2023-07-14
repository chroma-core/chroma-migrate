import os
from typing import Dict
import duckdb
from chromadb.api import API
from chromadb.api.models.Collection import Collection
from tqdm import tqdm
import json

def migrate_from_duckdb(api: API, persist_directory: str):
    # Load all the collections from the parquet files
    if not os.path.exists(persist_directory):
        raise Exception(f"Persist directory {persist_directory} does not exist")

    conn = duckdb.connect(read_only=False)

    print("Loading Existing Collections...")
    # Load the collections into duckdb
    collections_parquet_path = os.path.join(persist_directory, "chroma-collections.parquet")
    conn.execute(
            "CREATE TABLE collections (uuid STRING, name STRING, metadata STRING);"
        )
    conn.execute(
        f"INSERT INTO collections SELECT * FROM read_parquet('{collections_parquet_path}');"
    )

    # Read the collections from duckdb
    collections = conn.execute("SELECT uuid, name, metadata FROM collections").fetchall()

    # Create the collections in chromadb
    print("Migrating existing collections...")
    collection_uuid_to_chroma_collection: Dict[str, Collection] = {}
    for collection in collections:
        uuid, name, metadata = collection
        metadata = json.loads(metadata)
        coll = api.get_or_create_collection(name, metadata)
        collection_uuid_to_chroma_collection[uuid] = coll

    # -------------------------------------
    
    # Load the embeddings into duckdb
    print("Creating Embeddings")
    embeddings_parquet_path = os.path.join(persist_directory, "chroma-embeddings.parquet")
    conn.execute(
        "CREATE TABLE embeddings (collection_uuid STRING, uuid STRING, embedding DOUBLE[], document STRING, id STRING, metadata STRING);"
    )
    conn.execute(
        f"INSERT INTO embeddings SELECT * FROM read_parquet('{embeddings_parquet_path}');"
    )

    # Read the embeddings from duckdb
    embeddings = conn.execute("SELECT uuid, collection_uuid, id, embedding, document, metadata FROM embeddings").fetch_df()

    # Add the embeddings to the collections
    for record in tqdm(embeddings.itertuples(index=False), total=embeddings.shape[0]):
        uuid, collection_uuid, id, embedding, document, metadata = record
        metadata = json.loads(metadata)
        collection = collection_uuid_to_chroma_collection[collection_uuid]
        collection.add(id, embedding, metadata, document)

    return collections, embeddings


