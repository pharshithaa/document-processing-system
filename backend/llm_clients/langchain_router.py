from langchain_core.runnables import RunnableLambda, RunnableBranch
from llm_clients.gemini import extract_from_scanned_pdf, extract_from_large_document
from llm_clients.ollama import (
    extract_financial_data_with_llama,
    extract_legal_data_with_llama,
    extract_with_llama
)
from llm_clients.tinyllama import process_small_document

# Wrap each LLM function as a RunnableLambda
scanned_runnable = RunnableLambda(lambda inp: (extract_from_scanned_pdf(inp["file_path"]), "Scanned PDF processing"))
large_runnable = RunnableLambda(lambda inp: (extract_from_large_document(inp["file_path"]), "Large document processing"))
financial_runnable = RunnableLambda(lambda inp: (extract_financial_data_with_llama(inp["file_path"]), "Financial data extraction"))
legal_runnable = RunnableLambda(lambda inp: (extract_legal_data_with_llama(inp["file_path"]), "Legal document processing"))
small_runnable = RunnableLambda(lambda inp: (process_small_document(inp["file_path"]), "Small document processing"))
default_runnable = RunnableLambda(lambda inp: (extract_with_llama(inp["file_path"]), "General analysis"))

# Conditions as standalone functions
def is_scanned(inp):
    return inp["metadata"].get("is_scanned", False)

def is_financial(inp):
    return inp["helpers"]["contains_financial_tables"](inp["file_path"])

def is_large(inp):
    return inp["metadata"].get("pages", 0) > 10

def is_small(inp):
    return inp["metadata"].get("pages", 0) <= 3

def is_legal(inp):
    return inp["helpers"]["is_legal_document"](inp["file_path"])

class LangChainRouter:
    def __init__(self):
        self.router = RunnableBranch(
            (is_scanned, scanned_runnable),
            (is_large, large_runnable),
            (is_financial, financial_runnable),
            (is_legal, legal_runnable),
            (is_small, small_runnable),
            default_runnable  # fallback
        )

    def route(self, file_path, metadata, helpers):
        inp = {"file_path": file_path, "metadata": metadata, "helpers": helpers}
        return self.router.invoke(inp)
