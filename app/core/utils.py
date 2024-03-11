import json
import os

import fitz
from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_core.runnables import RunnableSerializable
from langchain_experimental.text_splitter import SemanticChunker

from app.core import part_one, part_two

load_dotenv('.venv/.env')


async def extract_text_from_pdf(file_path):
    try:
        pdf_doc = fitz.open(file_path)
        extracted_text = ""
        for page in pdf_doc:
            extracted_text += page.get_text("text")
        return extracted_text
    except Exception as e:
        return f"Error extracting text: {str(e)}"


async def process_pdf_with_semantic_chunking(embeddings, text):
    # Initialize SemanticChunker
    text_splitter = SemanticChunker(embeddings)

    # Create documents
    docs = text_splitter.create_documents([text])

    return docs


async def evaluate(chain: RunnableSerializable[dict, str], question: str, docs: list[Document]):
    if question in part_one['questions'].keys():
        answer = await chain.ainvoke({'question': question, 'docs': docs,
                                      'options': part_one['questions'][question]['options'].keys(),
                                      'examples': part_one['questions'][question]['examples'],
                                      'notes': part_one['questions'][question]['notes']})
    else:
        answer = await chain.ainvoke({'question': question, 'docs': docs,
                                      'options': part_two['questions'][question]['options'].keys(),
                                      'examples': part_two['questions'][question]['examples'],
                                      'notes': part_two['questions'][question]['notes']})
    # print(answer)
    return answer.replace('\'', '').replace('\"', '')


async def convert_to_list_of_dicts(input_dict: dict) -> json:
    output_list = []
    for question, data in input_dict.items():
        output_list.append({
            "Question": question,
            "Answer": data["answer"],
            "Score": float(data["score"])  # Convert score to float
        })
    return json.dumps(output_list)


async def generate_reasons_for_rejection(chain, segments):
    return await chain.ainvoke({'segments': segments})
