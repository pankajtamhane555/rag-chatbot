import os
from langchain_community.document_loaders import PyPDFLoader  # Updated import
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone, ServerlessSpec
from .config import PINECONE_API_KEY, OPENAI_API_KEY, PINECONE_INDEX_NAME, PINECONE_ENV


# Initialize Pinecone
pinecone_client = Pinecone(api_key=PINECONE_API_KEY, environment=PINECONE_ENV)
index_name = PINECONE_INDEX_NAME

def load_chunk_persist_pdf(file_path, user_id):
    """
    Load a PDF file, split it into chunks, and persist the chunks in Pinecone.
    
    Args:
        file_path (str): The path to the PDF file.
        user_id (str): The ID of the user for creating a namespace.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File {file_path} not found.")
        
    if file_path.endswith('.pdf'):
        try:
            loader = PyPDFLoader(file_path)
            document = loader.load()
        except Exception as e:
            print("Error:", e)
        text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=10)
        chunked_documents = text_splitter.split_documents(document)
        get_or_create_user_vectorstore(chunked_documents, user_id)


def get_or_create_user_vectorstore(chunked_documents, user_id):
    """
    Create or retrieve a Pinecone vectorstore for the user and store documents.
    
    Args:
        chunked_documents (list): List of chunked documents to store.
        user_id (str): The ID of the user to create a namespace.
        
    Returns:
        vectordb: The Pinecone vectorstore.
    """
    try:
        embedding_model = OpenAIEmbeddings(model="text-embedding-ada-002", openai_api_key=OPENAI_API_KEY)

        existing_indexes = [index_info["name"] for index_info in pinecone_client.list_indexes()]

        # Check if the index exists, if not, create it
        if index_name not in existing_indexes:
            print("Index not found, creating new index...")
            pinecone_client.create_index(
                index_name, dimension=1536, metric='cosine',
                spec=ServerlessSpec(cloud='aws', region=PINECONE_ENV)
            )

        # Generate the namespace for the user
        namespace = f"user_{user_id}"

        # Check if the namespace exists and has vectors
        index = pinecone_client.Index(index_name)
        stats = index.describe_index_stats()
        namespace_exists = namespace in stats['namespaces']

        vectordb = None
        if namespace_exists:
            # Add new documents to the existing namespace
            vectordb = PineconeVectorStore(
                index=index,
                embedding=embedding_model,
                namespace=namespace
            )
            vectordb.add_documents(chunked_documents)
        else:
            print("Namespace does not exist, creating new namespace...")
            # Create the namespace and add documents
            vectordb = PineconeVectorStore.from_documents(
                chunked_documents,
                embedding_model,
                index_name=index_name,
                namespace=namespace
            )
        
        return vectordb
    except Exception as e:
        print("Error:", e)


def is_namespace_exist(user_id):
    """
    Check if a namespace exists in the Pinecone index for a user.
    
    Args:
        user_id (str): The ID of the user.
        
    Returns:
        bool: True if the namespace exists, False otherwise.
    """
    namespace = f"user_{user_id}"
    index = pinecone_client.Index(index_name)
    stats = index.describe_index_stats()

    return namespace in stats["namespaces"]
