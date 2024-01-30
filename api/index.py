import os
from PyPDF2 import PdfReader
from flask import Flask, request, jsonify
from flask_cors import CORS
from langchain import hub
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.llms.huggingface_hub import HuggingFaceHub
from langchain_community.vectorstores import FAISS

huggingfacehub_api_token = os.environ.get('HUGGINGFACEHUB_API_TOKEN')
repo_id = "google/flan-t5-xxl"  # See https://huggingface.co/models?pipeline_tag=text-generation&sort=downloads for some other options

app = Flask(__name__)
CORS(app)

# Define the path to the pre-trained model you want to use
modelPath = "sentence-transformers/all-MiniLM-l6-v2"

# Create a dictionary with model configuration options, specifying to use the CPU for computations
model_kwargs = {'device':'cpu'}

# Create a dictionary with encoding options, specifically setting 'normalize_embeddings' to False
encode_kwargs = {'normalize_embeddings': False}

# Initialize an instance of HuggingFaceEmbeddings with the specified parameters
embeddings = HuggingFaceEmbeddings(
    model_name=modelPath,     # Provide the pre-trained model's path
    model_kwargs=model_kwargs, # Pass the model configuration options
    encode_kwargs=encode_kwargs # Pass the encoding options
)

# Specify the model name you want to use
model_name = "Intel/dynamic_tinybert"

llm = HuggingFaceHub(repo_id="google/flan-t5-xxl", model_kwargs={"temperature":0.5, "max_length":512})

from langchain.chains import RetrievalQA
# Loads the latest version
prompt = hub.pull("rlm/rag-prompt", api_url="https://api.hub.langchain.com")

@app.route('/api/process', methods=['POST'])
def process_files():
    files = request.files.getlist('files')
    query = request.form.get('query')

    # Convert files to text
    text = ""
    for pdf in files:
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            text += page.extract_text()  # extracting text from each page
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=500,
        chunk_overlap=200,  # if any chunk ends in between of a sentence, so this will
        # make sure to end the chunk before; so that we dont lose any relevant information
        length_function=len
    )
    chunks = text_splitter.split_text(text)
    db = FAISS.from_texts(chunks, embeddings)

    qa_chain = RetrievalQA.from_chain_type(
        llm,
        retriever=db.as_retriever(),
        chain_type_kwargs={"prompt": prompt}
    )

    result = qa_chain({"query": query})['result']

    return jsonify({"result": result})


if __name__ == '__main__':
    app.run(debug=True, port=5328)
