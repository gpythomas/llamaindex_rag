# llamaindex_rag
This is a RAG chatbot built with llamaindex, with an OpenAI compative API written in Flask. There is nothing special about it but the API was written to make it easy to use with Obsidian's [Text Generator plugin](https://github.com/nhaouari/obsidian-textgenerator-plugin).

**Note: No encryption has been implemented in the API. The `chat_server.py` server script is meant to serve the API on localhost on a private network, it is not meant to serve the API on the web (use at your own risk).**

How to use:

1. Open `create_db.py` and `chat_server.py` and adjust the configuration (notably: API keys)
2. Create your vector storage with `create_db.py`
   - Optional: test the vector storage with `test_db.ipynb`
3. Start your chatbot API server locally with `chat_server.py`
   - Optional: test the API server with `test_db.ipynb`
4. If using Obsidian Text Generator, set your LLM provider as OpenAI and enter the chatbot API information there

See [here](Howto.md) for more detailed instructions.    
