# utils.py

def prepare_context(documents):
    context = []
    for doc in documents:
        file_name = doc.metadata.get("source", "Unknown")
        page_number = doc.metadata.get("page", "Unknown")
        page_content = doc.page_content

        context.append({
            "file_name": file_name,
            "page_number": page_number,
            "content": page_content
        })

    return context

def format_context(structured_context):
    return "\n".join(
        f"File: {item['file_name']}, Page: {item['page_number']}\n{item['content']}\n"
        for item in structured_context
    )

def extract_source_and_page(chunks):
    """Extract the source and page from each document chunk and join them with a newline."""
    results = []
    
    for chunk in chunks:
        # Use dot notation to access metadata and then dictionary-style to get source and page
        source = chunk.metadata.get('source', 'Unknown Source')
        page = chunk.metadata.get('page', 'Unknown Page')
        # Append the formatted string to results
        results.append(f"Source: {source}, Page: {page}")
    
    # Join the list of results into a single string, each on a new line
    return "\n".join(results)
    
def truncate_context(context, max_tokens=2000):
    """Truncate context to fit within a specific token limit."""
    # Split the context into words (or tokens, depending on your tokenizer)
    words = context.split()
    
    # If the context exceeds the maximum token limit, truncate it
    if len(words) > max_tokens:
        truncated_context = ' '.join(words[:max_tokens])
        print(f"Context truncated to {max_tokens} tokens.")
        return truncated_context
    
    # Return the original context if it's within the token limit
    return context
