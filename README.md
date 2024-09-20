# PDF Query Chatbot

This application leverages natural language processing and vector databases to provide a semantic search interface for PDF documents. Users can upload multiple PDFs and query their content using natural language prompts.

## Architecture

The application consists of two main components which are containerized using docker-compose:

1. **Backend**: A Flask-based server handles file uploads, PDF processing, and embedding management using Pinecone's vector database inegrated in langchain and openai's gpt-4o model.
2. **Frontend**: A Streamlit application provides a user-friendly interface for interacting with the chatbot.

## Key Features

- **Session Authentication**: Users enter a unique session ID, with the system checking for existing namespaces in Pinecone to prevent duplicates.
- **Multi-File Upload**: Support for simultaneous upload of multiple PDF files.
- **PDF Processing**: Automatic extraction and vectorization of PDF content.
- **Semantic Search**: Utilizes OpenAI embeddings for intelligent querying of PDF content.
- **Conversational Interface**: Chatbot-style interaction for querying uploaded documents.

## Technologies Used

- **Flask**: Web framework for the backend server
- **Streamlit**: Frontend framework for building the simple user interface
- **Pinecone**: A vector database for storing and retrieving document embeddings and performing similarity searches for each user separately.
- **OpenAI**: For generating text embeddings and provide answers based on the uploaded documents.
- **LangChain**: For effective implementation of RAG.

## Running Flask and Streamlit with Docker
- **Prerequisites**
    Docker and Docker Compose installed.
- **Project Structure**
    project-directory/
    ├── backend/
    │   ├── Dockerfile
    │   ├── main.py
    │   └── requirements.txt
    ├── frontend/
    │   ├── Dockerfile
    │   ├── app.py
    │   └── requirements.txt
    ├── docker-compose.yml
    └── .env
- **Step 1**: Build and Run
    1. Clone github repo
    git clone 
    2. Navigate to the Project Directory:
    cd rag-chatbot
    
- **Step 2**: .env Setup
    OPENAI_API_KEY=""
    PINECONE_API_KEY=""
    PINECONE_INDEX_NAME=""
    PINECONE_ENVIRONMENT=""

- **Step 3**: run project
    1. Build and Start Services:
    docker-compose up --build
    4. Access Applications:
    Flask: http://localhost:5000
    Streamlit: http://localhost:8501

- **Step 2**: Stop Containers
    1. To stop the services:
    docker-compose down