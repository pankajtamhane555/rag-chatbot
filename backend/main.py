import os
import tempfile
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
from .vector_db import load_chunk_persist_pdf, is_namespace_exist
from .chatbot import search_pdf_embeddings

app = Flask(__name__)
CORS(app)

@app.route('/check_namespace', methods=['POST'])
def check_namespace():
    """
    Check if the namespace exists in the Pinecone vector store for a given user.
    """
    user_id = request.json.get('user_id')
    
    if not user_id:
        return jsonify({'status': 'error', 'message': 'User ID is required.'}), 400

    # Check if the namespace exists in the index
    if is_namespace_exist(user_id):
        return jsonify({"exists": True}), 200
    else:
        return jsonify({"exists": False}), 200


@app.route('/upload', methods=['POST'])
def upload_pdfs():
    """
    Upload multiple PDF files, process them, and store their embeddings for the user.
    """
    # Get user ID from the form data
    user_id = request.form.get('user_id')
    if not user_id:
        return jsonify({'status': 'error', 'message': 'User ID is required.'}), 400

    # Get the uploaded files
    files = request.files.getlist('files')
    if not files or all(file.filename == '' for file in files):
        return jsonify({'status': 'error', 'message': 'No files provided.'}), 400

    try:
        # Create a temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            for file in files:
                # Ensure only PDF files are allowed
                if not file.filename.lower().endswith('.pdf'):
                    return jsonify({'status': 'error', 'message': f'Only PDF files are allowed. {file.filename} is not a PDF.'}), 400

                # Secure the filename to prevent any malicious filename attacks
                filename = secure_filename(file.filename)
                
                # Create the full path for the file
                file_path = os.path.join(temp_dir, filename)
                
                # Save the uploaded file with its original name in the temporary directory
                file.save(file_path)
                print(f"Processing file: {filename}")

                # Process the file and store its embeddings
                load_chunk_persist_pdf(file_path, user_id)

                print(f"Finished processing: {filename}")

            # All files will be automatically deleted when we exit the with block

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

    return jsonify({'status': 'success', 'message': 'All files uploaded and processed successfully.'}), 200


@app.route('/query', methods=['POST'])
def query_pdf():
    """
    Query the uploaded PDF and return the answer to the question.
    """
    data = request.json
    query = data.get('question')
    user_id = data.get('user_id')

    if not query or not user_id:
        return jsonify({'status': 'error', 'message': 'Query and user_id are required.'}), 400

    try:
        # Perform the search and get the answer
        answer = search_pdf_embeddings(user_id, query)
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

    return jsonify({'status': 'success', 'answer': answer}), 200


if __name__ == '__main__':
    app.run(debug=True)
