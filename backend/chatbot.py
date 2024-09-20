from langchain_openai import OpenAIEmbeddings
from langchain.chains.question_answering import load_qa_chain
from langchain_community.chat_models import ChatOpenAI
from langchain_pinecone import PineconeVectorStore
from .config import OPENAI_API_KEY, PINECONE_INDEX_NAME


# Initialize embedding model
embedding_model = OpenAIEmbeddings(model="text-embedding-ada-002", openai_api_key=OPENAI_API_KEY)

def search_pdf_embeddings(user_id, query, top_k=3):
    """
    Search the vector store for relevant documents using a query and perform question answering.
    
    Args:
        user_id (str): The ID of the user (namespace).
        query (str): The search query.
        top_k (int): Number of top documents to retrieve.
        
    Returns:
        str: The answer generated by the QA chain.
    """
    print("Query:", query)
    
    try:
        # Load the vector database for the specific user
        vectordb = PineconeVectorStore(
            embedding=embedding_model,
            index_name=PINECONE_INDEX_NAME,
            namespace=f"user_{user_id}"
        )
    except Exception as e:
        raise RuntimeError(f"Failed to load vector store for user {user_id}: {e}")
    
    # Perform the search query on the vector store
    try:
        score_cutoff = 0.8
        results = vectordb.similarity_search_with_score(query=f"{query}",k=top_k)
        docs = []
        for doc, score in results:
            # if score > score_cutoff:
            docs.append(doc)
            print(f"* [SIM={score:3f}] {doc.page_content} [{doc.metadata}]")
    except Exception as e:
        raise RuntimeError(f"Error performing similarity search: {e}")
    
    print("Matching Docs:", docs)
    # Initialize the language model
    llm = ChatOpenAI(model="gpt-4o", temperature=0, openai_api_key=OPENAI_API_KEY)
    
    # Load and run the QA chain
    chain = load_qa_chain(llm, chain_type="stuff")
    result = chain.run(input_documents=docs, question=query)
    
    return result
