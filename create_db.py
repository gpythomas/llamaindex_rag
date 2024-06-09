import os

import openai
from llama_index.embeddings.openai import OpenAIEmbedding

from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext, Settings
from llama_index.core.node_parser import TokenTextSplitter, MarkdownNodeParser, SimpleNodeParser
from llama_index.core.extractors import TitleExtractor
from llama_index.core.ingestion import IngestionPipeline, IngestionCache

import chromadb
from llama_index.vector_stores.chroma import ChromaVectorStore # pip install llama-index-vector-stores-chroma

import logging
logging.basicConfig(filename='create_db.log', level=logging.DEBUG)

## a nice tutorial intro to llamaindex: https://nanonets.com/blog/llamaindex/

## load embedding model 
# https://docs.llamaindex.ai/en/stable/module_guides/models/embeddings/
# https://docs.llamaindex.ai/en/stable/examples/embeddings/OpenAI/

openai.api_key = os.environ["OPENAI_API_KEY"]

## create database and document collection
# https://docs.llamaindex.ai/en/stable/understanding/storing/storing/
# https://docs.llamaindex.ai/en/latest/examples/vector_stores/chroma_metadata_filter/

# initialize client, setting path to save data
db = chromadb.PersistentClient(path="./chroma_db")

# create collection
collection_name = "MyCollection"

try:
    db.delete_collection(name=collection_name) # delete previous collection with same name
except:
    print(f"No existing collection with name {collection_name}") 

chroma_collection = db.get_or_create_collection(collection_name)

## create documents, parse into nodes and ingest

# load some documents
documents = SimpleDirectoryReader("./rag_docs").load_data()

# assign chroma as the vector_store to the context
vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
storage_context = StorageContext.from_defaults(vector_store=vector_store)

# create pipeline for document ingestion
# https://docs.llamaindex.ai/en/stable/module_guides/indexing/vector_store_index/
# https://docs.llamaindex.ai/en/stable/module_guides/loading/ingestion_pipeline/transformations/
# https://docs.llamaindex.ai/en/stable/module_guides/loading/node_parsers/modules/

parser = SimpleNodeParser.from_defaults(chunk_size=1024, chunk_overlap=20)
nodes = parser.get_nodes_from_documents(documents)

index = VectorStoreIndex(
    nodes,
    embed_model=OpenAIEmbedding(model="text-embedding-3-small"),
    storage_context=storage_context
)

print(f"Ingested {len(nodes)} Nodes")