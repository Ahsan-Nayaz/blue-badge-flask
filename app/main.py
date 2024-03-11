import asyncio
import json
import os
import uuid

from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableSerializable
from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings
from quart import Quart, render_template, session, redirect, jsonify, request
# from quart_session import Session
from werkzeug.utils import secure_filename

from app.core import *

load_dotenv('.venv/.env')

MAX_TOKEN = 1200
TEMPERATURE = 0.0

app = Quart(__name__)
# app.config['SESSION_TYPE'] = 'memcached'
# app.config['SESSION_PROTECTION'] = True
# Session(app)
app.secret_key = os.getenv("SESSION_SECRET_KEY")  # Set a secret key for session management

llm = AzureChatOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    openai_api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    azure_deployment="gpt-4-1106",
    openai_api_version="2023-09-01-preview",
)
embeddings = AzureOpenAIEmbeddings(
    azure_endpoint=os.getenv('AZURE_OPENAI_ENDPOINT'),
    openai_api_key=os.getenv('AZURE_OPENAI_API_KEY'),
    openai_api_version='2023-09-01-preview'
)


@app.route('/')
async def index():
    is_authenticated = session.get('is_authenticated')
    if is_authenticated == 'True':
        session['user_id'] = uuid.uuid4()
        return await render_template('main.html')
    else:
        return redirect('login')


@app.route('/login')
async def login():
    is_authenticated = session.get('is_authenticated')
    if is_authenticated == 'True':
        return redirect('/')
    return await render_template('login.html')


@app.post('/logout')
async def logout():
    session['is_authenticated'] = 'False'
    return redirect('/login')


@app.post('/login')
async def handle_login():
    username = (await request.form)['username']
    password = (await request.form)['password']
    user = await authenticate_user(username, password)
    if not user:
        error = 'Please enter a valid username and password'
        return await render_template('login.html', username=username, password=password,
                                     error=error)
    else:
        session['is_authenticated'] = 'True'
        return redirect('/')


@app.post('/extract-text')
async def extract_text():
    file = (await request.files)['file']
    if file:
        user_id = session.get('user_id')
        if user_id is None:
            return {"status": 'error', "message": 'User ID not found in session'}
        # Create the directory if it doesn't exist
        directory = os.path.join('.files', str(user_id))
        os.makedirs(directory, exist_ok=True)
        # Save the file to the temporary directory
        file_path = os.path.join(directory, secure_filename(file.filename))
        await file.save(file_path)
        # Extract text from the PDF
        extracted_text = await extract_text_from_pdf(file_path)
        # Store the extracted text in the session
        session['extracted_text'] = extracted_text
        # docs: list[Document] = await process_pdf_with_semantic_chunking(embeddings, extracted_text)
        # print(docs)
        # db = await Chroma.afrom_documents(docs, embeddings, persist_directory="./chroma_db")
        # session['db'] = db
        return {"status": 'success', "message": 'File uploaded successfully', "extracted_text": extracted_text}

    return {"status": 'error', "message": 'File not valid'}


@app.get('/analyze-pdf')
async def analyze_text():
    extracted_text: str = session.get('extracted_text')
    # db = Chroma(persist_directory="./chroma_db", embedding_function=embeddings)
    if extracted_text:
        part_one_prompt: ChatPromptTemplate = ChatPromptTemplate.from_template(SCORING_PROMPT)
        chain: RunnableSerializable[dict, str] = part_one_prompt | llm | StrOutputParser()

        async def evaluate_question(chain, question, docs):
            answer = await evaluate(chain, question, docs)
            return {
                "question": question,
                "answer": answer,
                "score": part_one['questions'][question]['options'][answer]
            }

        # Parallelize question evaluation
        tasks = [evaluate_question(chain, question, extracted_text) for question in part_one['questions'].keys()]
        results = await asyncio.gather(*tasks)
        total_marks = sum(item['score'] for item in results)
        df_json = json.dumps(results)
        session['total_marks'] = total_marks
        if total_marks < 40:
            rejected_sections = {item['question']: {'answer': item['answer'], 'score': item['score']} for item in
                                 results if item['score'] == 0}
            # if not rejected_sections.empty:
            rejection_prompt = ChatPromptTemplate.from_template(REJECTION_PROMPT)
            chain = rejection_prompt | llm | StrOutputParser()
            reason = await generate_reasons_for_rejection(chain, rejected_sections)
            return jsonify({'data': df_json, "status": "failed", "score": total_marks, "reason": reason})
        else:
            return jsonify({'data': df_json, "status": "passed", "score": total_marks})


@app.get('/check-round-two')
async def check_for_round_two():
    extracted_text: str = session.get('extracted_text')
    # db = Chroma(persist_directory="./chroma_db", embedding_function=embeddings)
    if extracted_text:
        part_two_prompt: ChatPromptTemplate = ChatPromptTemplate.from_template(SCORING_PROMPT)
        chain: RunnableSerializable[dict, str] = part_two_prompt | llm | StrOutputParser()

        async def evaluate_question(chain, question, docs):
            answer = await evaluate(chain, question, docs)
            return {
                "question": question,
                "answer": answer,
                "score": part_two['questions'][question]['options'][answer]
            }

        # Parallelize question evaluation
        tasks = [evaluate_question(chain, question, extracted_text) for question in part_two['questions'].keys()]
        results = await asyncio.gather(*tasks)
        total_marks = float(session.get('total_marks'))
        total_marks += sum(item['score'] for item in results)
        df_json = json.dumps(results)
        session['total_marks'] = total_marks
        if total_marks < 60:
            rejected_sections = {item['question']: {'answer': item['answer'], 'score': item['score']} for item in
                                 results if item['score'] == 0}
            # if not rejected_sections.empty:
            rejection_prompt = ChatPromptTemplate.from_template(REJECTION_PROMPT)
            chain = rejection_prompt | llm | StrOutputParser()
            reason = await generate_reasons_for_rejection(chain, rejected_sections)
            return jsonify({'data': df_json, "status": "failed", "total_score": total_marks, "reason": reason})
        else:
            return jsonify({'data': df_json, "status": "passed", "total_score": total_marks})
