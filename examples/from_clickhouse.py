# This example shows how to use chroma_migrate to migrate from a chroma database stored in clickhouse to a chroma database stored locally

from chroma_migrate.import_clickhouse import migrate_from_clickhouse

# Instantiate a chroma client that we wish to migrate to
import chromadb
api = chromadb.PersistentClient(path="./chroma_data")

# Migrate from clickhouse to the chroma client, assuming our old data was stored in the clickhouse server at localhost:8123
migrate_from_clickhouse(api, "localhost", 8123)