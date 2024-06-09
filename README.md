# llamaindex_rag
This is a RAG chatbot built with llamaindex, with an OpenAI compative API written in Flask. It should work with Obsidian's [Text Generator plugin](https://github.com/nhaouari/obsidian-textgenerator-plugin) by selecting `OpenAI Chat` as LLM provider in the plugin settings.  

Note: this is a chatbot that I used specifically to interact with Obsidian Text Generator's plugin on my desktop. The API server is meant to run on localhost. It's probably not a good idea to run it on the web (use at your own risk).

How to use:

1. Optional: create a python virtual environment: [venv — Creation of virtual environments](https://docs.python.org/3/library/venv.html)
2. Install the python depencies using requirements file: [How to install Python packages with pip and requirements.txt](https://note.nkmk.me/en/python-pip-install-requirements/)
   - you should also install the following packaes, which were not captured by pipreqs:
      - llama-index-vector-stores-chroma (pip install llama-index-vector-stores-chroma)
      - llama_index.llms.openrouter (pip install llama_index.llms.openrouter)
3. Use llama-index-rag.ipynb to create your vector storage and test it:
    - put the documents you'd like to add to your vector storage inside rag_docs; plain text is better than PDF, see [PDF Hell and Practical RAG Applications](https://unstract.com/blog/pdf-hell-and-practical-rag-applications/). I like [PyMuPDF](https://pymupdf.readthedocs.io) for text extraction.
    - here is some information on how to run python notebooks in VSCode: [Jupyter Notebooks in VS Code](https://code.visualstudio.com/docs/datascience/jupyter-notebooks)
    - run the notebook cell by cell, installing any missing dependencies if missing from the requirements file
      - you can set `embed_model` and `llm` to some models other than the ones used in the notebook
      - you will need to provide your API key for the embedding model (`embed_model`) and chat model (`llm`); in the script, both models are from OpenAI and the API key is stored as an environment variable `OPENAI_API_KEY`. You can write your API key in the script if you want, although it's better practice to put it in an enviroment variable. Here is how you can do that on different OSes: [Best Practices for API Key Safety](https://help.openai.com/en/articles/5112595-best-practices-for-api-key-safety)
      - note that you can configure chunk size and overlap as explained here: [Loading Data (Ingestion)](https://docs.llamaindex.ai/en/stable/understanding/loading/loading/)
4. Open chat_server.py and adjust the configuration:
    - at that point, you should have a chroma_db subfolder in your app folder; this was created in step 3 and contains your vector storage
    - before you run the chat_server.py script, you should open it and adjust the configuration:
      - in `collection_name = "Your_collection_name"`, use the name of the collection you created in 3
      - the version of the script provided in this repository uses OpenAI as an embedding model provider and OpenRouter as a chat model provider; you can change that as you need, but if you select a chat model provider whose API is not OpenAI compatible, you might need to adjust the script to reflect your provider's API
       - make sure that you use the same embedding model than the one you used to create the vector store
       - you will need to provide an API key for the chat model, in the script it's stored as an environment variable `OPENROUTER_API_KEY`; if you change to a provider other than OpenRouter, you will also need to change the value of the base URL variable (in the script, `OPENROUTER_API_URL`)
       - the API server has a key (`API_KEY`), which is set to the dummy value "you_api_key_here" by default; change that to whatever you want;
       - the API server port is set to 8080 at the very bottom of the script, change that to whatever port you prefer
5. Run chat_server.py to serve on localhost:
    - at this point, should should be good to run the script by typing `python chat_server.py` in a terminal
    - the script will create an OpenAI compatible API for your RAG on locahost
    - you might want to make sure that your firewall is not blocking connections to localhost and whatever port you chose
6. Use test_API.ipynb to test your API:
    - open the notebook and run the file cell by cell, it will test your API, including CORS settings
    - set the API server key (`API_KEY`) and base URL (`BASE_URL`) to whatever you picked in step 4
7. If you are using this with Obsidian Text Generator:
    - in TG LLM settings, choose OpenAI as a model provider
    - click the `+` icon next to the LLM provider box to create a new model profile, rename it as you wish
    - in `Base Path` enter `http://localhost:8080/v1`, changing the port number to whatever you picked in 3, if needed
    - in `API Key`, enter the API server API key that you defined in step 4 (that's the value of `API_KEY` in the chat_server.py script)
    - in `Model`, pick a model that is available on your model provider; the chat_server.py script as `microsoft/wizardlm-2-8x22b` as a default. In order to enter an non-OpenAI model, you need to click the pen icon next to the `Model` field and enter the model name manually
    - in `Advanced Setting`, you can leave `Streaming` unticked because I haven't implemented streaming yet
    - you can adjust the `Default model parameters` as you see fit

    
