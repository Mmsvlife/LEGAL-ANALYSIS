from flask import Flask, request, jsonify
from flask_cors import CORS
from document_processing import (
    load_documents_from_directory,
    load_or_create_vector_store,
    retrieve_and_answer_question,
    load_documents_from_markdown
)
from summarizer import summarize_case
from testcase import extract_case_metadata
from logging_config import logger
from config import COLLECTION_NAME, PERSIST_DIRECTORY

app = Flask(__name__)
CORS(app)  # This allows cross-origin requests, which is useful if your React app is hosted separately

'''
Request:
{
    "document_path": "",
    "user_id": ""
}

Response:
{
    "initial_findings": "",
    "followup_info": "",
    "final_summary": ""
}
'''
@app.route('/api/summary/generate', methods=['POST'])
def process_data():
    # Get the JSON data from the request body
    data = request.json

    # Extract the required fields
    document_path = data.get('document_path')
    # collection_id = data.get('collection_id')
    user_id = data.get('user_id')

    if not document_path:
        raise ValueError("Unable to process the request. Invalid directory path received.")
    if document_path.endswith(".md"):
        documents = load_documents_from_markdown(document_path)
    else:
        documents = load_documents_from_directory(document_path)

    vector_store = load_or_create_vector_store(documents)

    # Extract case metadata like date and parties
    logger.info("Extracting case metadata...")
    case_metadata = extract_case_metadata(documents)

    # Summarize the case
    summarized_result = summarize_case(
        question=f"Generate the complete summary of the document and provide a concise summary of the case and here is the case metadata for your better retrival Metadata : {case_metadata}",
        documents=documents, vector_store=vector_store)

    # sources = {}
    # for item in summarized_result['structured_context']:
    print(summarized_result)

    response = {
        "initial_findings": summarized_result['initial_findings'],
        "followup_info": summarized_result['followup_info'],
        "final_summary": summarized_result['final_summary']
    }

    return jsonify(response), 200

if __name__ == '__main__':
    app.run(debug=True)