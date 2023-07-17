# This example shows how to use chroma_migrate to migrate from a chroma database stored in duckdb to a chroma database stored locally

from chroma_migrate.import_duckdb import migrate_from_duckdb

# Instantiate a chroma client that we wish to migrate to
import chromadb
api = chromadb.PersistentClient(path="./chroma_data")

# Migrate from duckdb to the chroma client, assuming our old data was stored in the directory ./test_data_duckdb
migrate_from_duckdb(api, "./test_data_duckdb")