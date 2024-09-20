import streamlit as st
import requests

st.title('PDF Uploader and Query Tool')

# Initialize session state variables
if 'user_id' not in st.session_state:
    st.session_state.user_id = ""
if 'query' not in st.session_state:
    st.session_state.query = ""
if 'answer' not in st.session_state:
    st.session_state.answer = ""
if 'files_uploaded' not in st.session_state:
    st.session_state.files_uploaded = False

# Function to handle file upload
def handle_upload():
    if not st.session_state.files_uploaded and st.session_state.uploaded_files:
        st.write(f"Uploading {len(st.session_state.uploaded_files)} file(s).")
        files_to_upload = [('files', (file.name, file, 'application/pdf')) for file in st.session_state.uploaded_files]
        data = {'user_id': st.session_state.user_id}
        response = requests.post('http://flask-app:5000/upload', files=files_to_upload, data=data)
        if response.status_code == 200:
            st.write('Files processed successfully.')
            st.session_state.files_uploaded = True
        else:
            st.write('Error processing files.')

# Function to handle query submission
def handle_query():
    if st.session_state.query:
        response = requests.post('http://flask-app:5000/query', json={'question': st.session_state.query, 'user_id': st.session_state.user_id})
        if response.status_code == 200:
            st.session_state.answer = response.json().get('answer')
        else:
            st.session_state.answer = 'Error getting answer.'

# Function to set user ID
def set_user_id():
    user_id = st.session_state.user_id_input
    if user_id:
        response = requests.post('http://flask-app:5000/check_namespace', json={'user_id': user_id})
        if response.status_code == 200:
            namespace_exists = response.json().get("exists")
            if namespace_exists:
                st.error("Namespace already exists for this User ID. Please choose a different ID.")
            else:
                st.session_state.user_id = user_id
        else:
            st.error("Error checking namespace. Try again later.")

# User ID input
if st.session_state.user_id:
    st.text_input("User ID:", st.session_state.user_id, disabled=True)
else:
    st.text_input("Enter your Session ID:", key="user_id_input")
    if st.button('Set User ID'):
        set_user_id()

# Main application logic
if st.session_state.user_id:
    # File uploader
    if not st.session_state.files_uploaded:
        st.session_state.uploaded_files = st.file_uploader("Choose PDF files", accept_multiple_files=True, type='pdf')
        if st.button('Upload Files'):
            handle_upload()
    else:
        st.success("Files have been uploaded successfully. You can now ask questions about the PDFs.")

    # Query input
    st.text_input("Ask a question about the PDFs:", key="query")
    if st.button('Submit Query'):
        handle_query()

    # Display answer
    if st.session_state.answer:
        st.write('Answer:', st.session_state.answer)
else:
    st.warning("Please enter your User ID and click 'Set User ID'.")