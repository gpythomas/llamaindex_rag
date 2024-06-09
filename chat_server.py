# https://docs.llamaindex.ai/en/stable/understanding/putting_it_all_together/apps/fullstack_app_guide/
# https://docs.llamaindex.ai/en/stable/examples/chat_engine/chat_engine_openai/

import os
import requests
from llama_index.core import VectorStoreIndex
from llama_index.vector_stores.chroma import ChromaVectorStore
import chromadb
from llama_index.core import Settings
from llama_index.core.memory import ChatMemoryBuffer 
# Openai and openrouter
import openai
from llama_index.llms.openrouter import OpenRouter
from llama_index.embeddings.openai import OpenAIEmbedding
# Flask API
from flask import Flask, request, jsonify
from flask_cors import CORS
from functools import wraps
import uuid
import time

import logging
logging.basicConfig(filename='chat_server.log', level=logging.DEBUG)

# Openai API key
openai.api_key = os.environ["OPENAI_API_KEY"]

# Openrouter API key and base URL
OPENROUTER_API_KEY = os.environ["OPENROUTER_API_KEY"]
OPENROUTER_API_URL = 'https://openrouter.ai/api/v1'

# Embedding model
embed_model = OpenAIEmbedding(model="text-embedding-3-small")
Settings.embed_model = embed_model

# Chat completion model
# https://docs.llamaindex.ai/en/stable/examples/llm/openrouter/
# llm = OpenAI(model="gpt-4o")
def llm(model="microsoft/wizardlm-2-8x22b", max_tokens=600, temperature=1, top_p=1, top_k=0, frequency_penalty=0, presence_penalty=0, repetition_penalty=1, min_p=0, top_a=0):
    llm = OpenRouter(
        api_key=OPENROUTER_API_KEY,
        model=model,
        max_tokens=max_tokens,
        temperature=temperature,
        frequency_penalty=frequency_penalty,
        top_p=top_p,
        top_k=top_k,
        presence_penalty=presence_penalty,
        repetition_penalty=repetition_penalty,
        min_p=min_p,
        top_a=top_a
    )
    return llm

# Initialize index
index = None
def initialize_index():
    global index
    collection_name = "MyCollection"
    db = chromadb.PersistentClient(path="./chroma_db")
    chroma_collection = db.get_or_create_collection(collection_name)
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    index = VectorStoreIndex.from_vector_store(
        vector_store,
        embed_model=embed_model
    )

# Create chat engine
# https://docs.llamaindex.ai/en/stable/module_guides/deploying/chat_engines/
# https://docs.llamaindex.ai/en/latest/examples/chat_engine/chat_engine_context/

def chat_with_data(model, system_prompt, max_tokens, temperature, top_p, top_k, frequency_penalty, presence_penalty, repetition_penalty, min_p, top_a):
    memory = ChatMemoryBuffer.from_defaults(token_limit=1500)
    chat_engine = index.as_chat_engine(
        chat_mode="context",
        llm=llm(model, max_tokens, temperature, top_p, top_k, frequency_penalty, presence_penalty, repetition_penalty, min_p, top_a),
        memory=memory,
        system_prompt = system_prompt
    )
    return chat_engine

# create Flask API
# https://towardsdatascience.com/how-to-build-an-openai-compatible-api-87c8edea2f06

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}) # Configure CORS for the entire app

#@app.after_request
#def after_request(response):
#    response.headers.add('Access-Control-Allow-Origin', '*')
#    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
#    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
#    return response

# Example API key for authentication
API_KEY = "my_chat_server_key"

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.method == 'OPTIONS':
            return f(*args, **kwargs)
        if 'Authorization' not in request.headers:
            return jsonify({"error": "API key required"}), 401
        auth_header = request.headers['Authorization']
        if auth_header != f"Bearer {API_KEY}":
            return jsonify({"error": "Invalid API key"}), 403
        return f(*args, **kwargs)
    return decorated_function

def fetch_openrouter_models():
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}"
    }
    response = requests.get(OPENROUTER_API_URL + '/models', headers=headers)
    if response.status_code == 200:
        return response.json().get("data", [])
    else:
        raise Exception(f"Failed to fetch models from OpenAI API: {response.status_code} {response.text}")

@app.route('/v1/models', methods=['GET', 'OPTIONS'])
@require_api_key
def get_models():
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'})
    try:
        models = fetch_openrouter_models()
        return jsonify({"data": models})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/v1/chat/completions', methods=['POST', 'OPTIONS'])
@require_api_key
def chat_completions():
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'})
    try:
        data = request.json
        if not data or 'messages' not in data:
            return jsonify({"error": "Invalid request: 'messages' field is required"}), 400

        # Extract model parameters from the request
        model = data.get('model', 'default-model')
        max_tokens = data.get('max_tokens', 150)
        temperature = data.get('temperature', 1.0)
        top_p = data.get('top_p', 1.0)
        top_k = data.get('top_k', 50)
        frequency_penalty = data.get('frequency_penalty', 0.0)
        presence_penalty = data.get('presence_penalty', 0.0)
        repetition_penalty = data.get('repetition_penalty', 1.0)
        min_p = data.get('min_p', 0.0)
        top_a = data.get('top_a', 0.0)

        # Initialize lists to store different types of messages
        user_messages = []
        system_messages = []
        assistant_messages = []

        # Iterate through the messages and categorize them
        for message in data['messages']:
            role = message.get('role')
            content = message.get('content')
            if role == 'user':
                user_messages.append(content)
            elif role == 'system':
                system_messages.append(content)
            elif role == 'assistant':
                assistant_messages.append(content)

        # Generate responses for each message
        choices = []

        # Initialize variables to store the latest system prompt and user message

        latest_system_prompt = "You are a helpful and friendly chatbot"

        latest_user_message = None

        for i, message in enumerate(data['messages']):
            role = message.get('role')
            content = message.get('content')
            
            if role == 'system':
                # Update the latest system prompt
                latest_system_prompt = content
            elif role == 'user':
                # Update the latest user message
                latest_user_message = content
                
                # Initialize the chat engine using the chat_with_data function
                chat_engine = chat_with_data(model, latest_system_prompt, max_tokens, temperature, top_p, top_k, frequency_penalty, presence_penalty, repetition_penalty, min_p, top_a)
                
                # Generate the response
                response_content = chat_engine.chat(latest_user_message).response
                
                choice = {
                    "index": i,
                    "message": {
                        "role": "assistant",
                        "content": response_content
                    },
                    "finish_reason": "stop"
                }
                
                choices.append(choice)

        response = {
            "id": str(uuid.uuid4()),  # Generate a unique ID
            "object": "chat.completion",
            "created": int(time.time()),  # Current timestamp
            "model": model,  # Use provided model
            "choices": choices
        }

        return jsonify(response)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    initialize_index()
    app.run(host="0.0.0.0", port=8080, debug=True)