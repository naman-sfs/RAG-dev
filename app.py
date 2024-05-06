## INDEXING

# Step 0: Adding OpenAI API Key
import os

# Step 1: Loading the documents
from langchain_community.document_loaders import PyPDFLoader

loader = PyPDFLoader('./pdfs/PDF-1.pdf')
pages = loader.load_and_split()

print(type(pages))

# Step 2: Splitting the texts into smaller chunks
from langchain_text_splitters import RecursiveCharacterTextSplitter  # This splitter splits the chunks from the end of the line

text_splitter = RecursiveCharacterTextSplitter(chunk_size = 2000, chunk_overlap = 300, add_start_index = True)
chunks = text_splitter.split_documents(pages)
print(type(chunks[56]))


# Step 3: Store the chunks
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings

vectorstore = Chroma.from_documents(documents=chunks,embedding=GoogleGenerativeAIEmbeddings(model = "models/embedding-001"))
print(type(vectorstore))


#Retrieval and Generation

#Step 1: Retieval of similar documents from the vector store

retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 3})
retrieved_docs = retriever.invoke("How to be a good parent?")
for doc in retrieved_docs:
    print(doc.page_content)
    print("***************************************")
    
    
# Step 2: Generating

from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-3.5-turbo",temperature=0.4,max_tokens=1024)

from langchain import hub

prompt = hub.pull('rlm/rag-prompt')

from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough


def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

for chunk in rag_chain.stream("How to o/iobe a good parent?"):
    print(chunk, end="", flush=True)io

