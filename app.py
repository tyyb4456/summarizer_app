import os
import streamlit as st
from groq import Groq
import PyPDF2

# Initialize the Groq client with the API key
client = Groq(
    api_key=os.environ.get("smrz"),
)

# Function to summarize text using Groq's language model
def summarize_text(text, model="llama3-8b-8192"):
    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": f"Summarize this document: {text}"}],
        model=model,
    )
    return chat_completion.choices[0].message.content

# Function to read PDF using PyPDF2
def read_pdf(file):
    reader = PyPDF2.PdfReader(file)
    text = ""
    for page_num in range(len(reader.pages)):
        page = reader.pages[page_num]
        text += page.extract_text()
    return text

# Function to split text into smaller chunks
def split_text(text, max_length=2048):
    # Split text by words and keep chunks under the max_length
    words = text.split()
    chunks = []
    current_chunk = []
    current_length = 0
    
    for word in words:
        current_length += len(word) + 1  # Account for spaces between words
        if current_length > max_length:
            chunks.append(" ".join(current_chunk))
            current_chunk = [word]
            current_length = len(word)
        else:
            current_chunk.append(word)
    
    # Add the last chunk
    if current_chunk:
        chunks.append(" ".join(current_chunk))
    
    return chunks

# Streamlit UI for document summarizer
st.title("Document Summarizer")

# File upload widget
uploaded_file = st.file_uploader("Upload a document", type=["txt", "pdf"])

# If a file is uploaded
if uploaded_file is not None:
    # Process the text content
    file_content = uploaded_file.read()

    # If the file is a PDF, convert it to text using PyPDF2
    if uploaded_file.type == "application/pdf":
        text = read_pdf(uploaded_file)
    else:  # Assuming it's a text file
        text = file_content.decode("utf-8")

    # Show the content of the document
    st.subheader("Uploaded Document:")
    st.write(text[:2000])  # Show the first 2000 characters

    # Split the text into smaller chunks
    text_chunks = split_text(text, max_length=2048)

    # Button to summarize the document
    if st.button("Summarize"):
        summaries = []
        with st.spinner("Summarizing..."):
            for chunk in text_chunks:
                summary = summarize_text(chunk)
                summaries.append(summary)
        
        # Combine all summaries
        full_summary = " ".join(summaries)
        
        st.subheader("Summary:")
        st.write(full_summary)

else:
    st.info("Please upload a document to summarize.")