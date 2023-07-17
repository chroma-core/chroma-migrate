# This example shows how to use chroma_migrate to migrate from any chroma database accessed via HTTP to a chroma database stored locally

from chroma_migrate.import_chromadb import migrate_from_remote_chroma

# Instantiate a chroma client that we wish to migrate to
import chromadb
api = chromadb.PersistentClient(path="./chroma_data")

# Migrate from a chroma server to the chroma client, assuming our old data was stored in the chroma server at localhost:8000
old_api = chromadb.HttpClient(host="localhost", port=8000)
migrate_from_remote_chroma(old_api, api)