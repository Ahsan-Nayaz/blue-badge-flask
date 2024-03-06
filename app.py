from flask import Flask, render_template, request,session,jsonify,redirect,url_for
from werkzeug.utils import secure_filename
from langchain_community.embeddings import HuggingFaceInferenceAPIEmbeddings
from langchain_experimental.text_splitter import SemanticChunker
from openai import AzureOpenAI
from typing import Union
from pydantic import BaseModel
from werkzeug.security import check_password_hash
from passlib.hash import pbkdf2_sha256
import fitz
import pandas as pd
import os
import time
import re
from dotenv import load_dotenv

load_dotenv('.env')

MAX_TOKEN = 1200
TEMPERATURE = 0.0

app = Flask(__name__)

app.secret_key = os.getenv("session_secret_key")  # Set a secret key for session management

df = pd.read_excel('NSC_updated.xlsb',
                       names=['Questions', 'Reply', 'Full_Marks', 'Yes', 'No', "Don't Know", 'A', 'B'])

qs_list = df[~df['Reply'].isnull()][['Questions', 'Full_Marks']].values
df.fillna(0, inplace=True)

client = AzureOpenAI(
    api_key = os.getenv("openai_api_key"),
    api_version = os.getenv("api_version"),
    azure_endpoint = os.getenv("azure_endpoint")
    )

class User(BaseModel):
    username: str
    email: Union[str, None] = None
    full_name: Union[str, None] = None
    disabled: Union[bool, None] = None

class UserInDB(User):
    hashed_password: str

@app.route('/')
def index():
    is_authenticated = session.get('is_authenticated')
    if is_authenticated == 'True':
        return render_template('main.html')
    else:
        return redirect('login')

@app.route('/login')
def login():
    is_authenticated = session.get('is_authenticated')
    if is_authenticated == 'True':
        return redirect('/')
    return render_template('login.html')   

fake_users_db = {
    "bluebadge_agent": {
        "username": "bluebadge_agent",
        "full_name": "Blue Badge Agent",
        "email": "johndoe@example.com",
        "hashed_password": "$pbkdf2-sha256$29000$8H4PQWjtnTPmvBfC2Ntb6w$fVtH5PhKYOM1nIEw7iS0Vmiuv3.RdE9jqQQk2zYYvKc",
        "disabled": False,
    }
}


def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)


def authenticate_user(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
    if not user:
        return False
    if not pbkdf2_sha256.verify(password, user.hashed_password):
        return False
    return user

@app.post('/login')
def handle_login():
    user = authenticate_user(fake_users_db,request.form['username'],  request.form['password'])
    if not user:
        error = 'Please enter a valid username and password'
        return render_template('login.html', username=request.form['username'], password = request.form['password'], error=error)
    else:
        session['is_authenticated'] = 'True' 
        return redirect('/')
    

@app.post('/logout')
def logout():
    session['is_authenticated'] = 'False'
    return redirect('/login')
    
def generate_reasons_for_rejection(sections):
    reasons = []
    response3 = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "system", "content": sections}],
        temperature=TEMPERATURE,
        max_tokens=MAX_TOKEN,
        top_p=1
    )
    rejection_reasons = response3.choices[0].message.content
    return rejection_reasons

def extract_text_from_pdf(file):
    pdf_doc = fitz.open(stream=file.read(), filetype="pdf")
    extracted_text = ""
    for page in pdf_doc:
        extracted_text += page.get_text("text")
    return extracted_text

def chunk_text(text):
    # Define key phrases to identify sections
    key_phrases = ["Walking ability", "Balance, coordination or posture", "Excessive pain - further details", "Balance and coordination - further details", "When they get breathless"]

    # Initialize chunks dictionary
    chunks = {}

        # Iterate over key phrases to split text into chunks
    for i in range(len(key_phrases)):
        start = text.find(key_phrases[i])
        if i==len(key_phrases)-1:
            end = len(text)-1
        else:
            end = text.find(key_phrases[i + 1])    

        # Check for other indicators of section end if key phrase not found
        if start == -1:
            chunk_text=""
        if end == -1:
            l=i+1
            while(l<len(key_phrases)-1):
                end = text.find(key_phrases[l])
                l=+1
                if end != -1:
                    end = text.rfind("\n", 0, end)
                    break

                # If key phrase for next section not found, use end of text
                # end = len(text)
        else:
            # Find the nearest new line character before end index
            end = text.rfind("\n", 0, end)

        # Extract text between start and end indices
        chunk_text = text[start:end].strip()

        # Add chunk to dictionary with key as section heading
        chunks[key_phrases[i]] = chunk_text
        # print(f"chunks:----{chunk_text}")

    # Add last section
    last_key = key_phrases[-1]
    last_start = text.find(last_key)
    last_chunk = text[last_start:].strip()
    chunks[last_key] = last_chunk

    return chunks

def process_pdf_with_semantic_chunking(text):
    
    docs={}
    inference_api_key = os.getenv('inference_api_key')
    embeddings = HuggingFaceInferenceAPIEmbeddings(
        api_key=inference_api_key, model_name="avsolatorio/GIST-Embedding-v0"
    )

    # Initialize SemanticChunker
    text_splitter = SemanticChunker(embeddings)

    # Create documents
    docs = text_splitter.create_documents([text])

    return docs

def yes_no_unsure(text):
    response = client.chat.completions.create(
        model="gpt-4-32k",
        messages=[{"role": "system", "content": text}],
        temperature=0,
        max_tokens=1200,
        top_p=1
    )
    time.sleep(2)
    return response.choices[0].message.content

def score_different(txt, resp, df):
    filt_df = df[df['Questions'] == txt]
    
    if txt == 'Permanent disability or condition (expected not to improve for at least 3 years)?':
        pat1 = 'Yes'
        pat2 = 'No'
        
        if re.search(pat1, resp) is not None:
            return filt_df['Yes'].values[0]
        elif re.search(pat2, resp) is not None:
            return filt_df['No'].values[0]
        # elif re.search(pat3, resp) is not None:
        #     return filt_df["Don't Know"].values[0]

    elif txt == "Do your health conditions affect your walking all the time?":
        pat1 = 'Yes'
        pat2 = 'No'
        
        if re.search(pat1, resp) is not None:
            return filt_df['Yes'].values[0]
        elif re.search(pat2, resp) is not None:
            return filt_df['No'].values[0]
        
    elif txt == "Have you seen a healthcare professional for any falls in the last 12 months?":
        pat1 = 'Yes'
        pat2 = 'No'
        
        if re.search(pat1, resp) is not None:
            return filt_df['Yes'].values[0]
        elif re.search(pat2, resp) is not None:
            return filt_df['No'].values[0]

        
    elif txt == 'For how long can the applicant walk?':
        pat1 = "Can't walk"
        pat2 = '<1 min'
        pat3 = '1-5 mins'
        pat4 = '5-10 mins'
        pat5 = '>10 mins'
        if re.search(pat1, resp.lower()) is not None:
            return filt_df['Yes'].values[0]
        elif re.search(pat2, resp.lower()) is not None:
            return filt_df['No'].values[0]
        elif re.search(pat3, resp.lower()) is not None:
            return filt_df["Don't Know"].values[0]
        elif re.search(pat4, resp.lower()) is not None:
            return filt_df['A'].values[0]
        elif re.search(pat5, resp.lower()) is not None:
            return filt_df['B'].values[0]
        
    elif txt == 'How far is the applicant able to walk? ':
        pat1 = '<30 m'
        pat2 = '<80 m'
        pat3 = '>80 m'
        pat4 = "Don't Know"
        if re.search(pat1, resp) is not None:
            return filt_df['Yes'].values[0]
        elif re.search(pat2, resp) is not None:
            return filt_df['No'].values[0]
        elif re.search(pat3, resp) is not None:
            return filt_df["Don't Know"].values[0]
        elif re.search(pat4, resp.lower()) is not None:
            return filt_df['A'].values[0]
        else:
            return 0
        
    elif txt == 'Do you have help to get around?':
        pat1 = 'Yes'
        pat2 = 'No'
        pat3 = "Don't Know"
        if re.search(pat1, resp) is not None:
            return filt_df['Yes'].values[0]
        elif re.search(pat2, resp) is not None:
            return filt_df['No'].values[0]
        elif re.search(pat3, resp) is not None:
            return filt_df["Don't Know"].values[0]

def score(txt, resp, df):
    filt_df = df[df['Questions'] == txt]

    if txt == 'Is the way you walk or your posture affected by your condition?':
        pat1 = 'Yes'
        pat2 = 'No'
        
        if re.search(pat1, resp) is not None:
            return filt_df['Yes'].values[0]
        elif re.search(pat2, resp) is not None:
            return filt_df['No'].values[0]
        else:
            return filt_df["Don't Know"].values[0]
        
    elif txt == 'The applicant can walk around a supermarket, with the support of a trolley':
        pat1 = 'Yes'
        pat2 = 'No'
        
        if re.search(pat1, resp) is not None:
            return filt_df['Yes'].values[0]
        elif re.search(pat2, resp) is not None:
            return filt_df['No'].values[0]
        else:
            return filt_df["Don't Know"].values[0]
    
    elif txt == 'The applicant can walk up/down a single flight of stairs in a house':
        pat1 = 'Yes'
        pat2 = 'No'
        
        if re.search(pat1, resp) is not None:
            return filt_df['Yes'].values[0]
        elif re.search(pat2, resp) is not None:
            return filt_df['No'].values[0]
        else:
            return filt_df["Don't Know"].values[0]
    
    elif txt == 'The applicant can only walk around indoors':
        pat1 = 'Yes'
        pat2 = 'No'
        
        if re.search(pat1, resp) is not None:
            return filt_df['Yes'].values[0]
        elif re.search(pat2, resp) is not None:
            return filt_df['No'].values[0]
        else:
            return filt_df["Don't Know"].values[0]
    
    elif txt == 'The applicant can walk around a small shopping centre':
        pat1 = 'Yes'
        pat2 = 'No'
        
        if re.search(pat1, resp) is not None:
            return filt_df['Yes'].values[0]
        elif re.search(pat2, resp) is not None:
            return filt_df['No'].values[0]
        else:
            return filt_df["Don't Know"].values[0]
    
    elif txt == 'Does the applicant require pain medication':
        pat1 = 'Yes'
        pat2 = 'No'
        
        if re.search(pat1, resp) is not None:
            return filt_df['Yes'].values[0]
        elif re.search(pat2, resp) is not None:
            return filt_df['No'].values[0]
        else:
            return filt_df["Don't Know"].values[0]
    
    elif txt == 'When the applicant takes pain relief medication they can cope with the pain':
        pat1 = 'Yes'
        pat2 = 'No'
        
        if re.search(pat1, resp) is not None:
            return filt_df['Yes'].values[0]
        elif re.search(pat2, resp) is not None:
            return filt_df['No'].values[0]
        else:
            return filt_df["Don't Know"].values[0]
        
    elif txt == 'Even after taking pain relief medication the applicant must stop and take regular breaks':
        pat1 = 'Yes'
        pat2 = 'No'
        
        if re.search(pat1, resp) is not None:
            return filt_df['Yes'].values[0]
        elif re.search(pat2, resp) is not None:
            return filt_df['No'].values[0]
        else:
            return filt_df["Don't Know"].values[0]
    
    elif txt == 'Even after taking pain relief medication the pain makes the applicant physically sick':
        pat1 = 'Yes'
        pat2 = 'No'
        
        if re.search(pat1, resp) is not None:
            return filt_df['Yes'].values[0]
        elif re.search(pat2, resp) is not None:
            return filt_df['No'].values[0]
        else:
            return filt_df["Don't Know"].values[0]
    
    elif txt == 'Even after taking pain relief medication is frequently in so much pain that walking for more than 2 minutes is unbearable':
        pat1 = 'Yes'
        pat2 = 'No'
        
        if re.search(pat1, resp) is not None:
            return filt_df['Yes'].values[0]
        elif re.search(pat2, resp) is not None:
            return filt_df['No'].values[0]
        else:
            return filt_df["Don't Know"].values[0]
    
    elif txt == 'Does the applicant gets breathless when walking up a slight hill?':
        pat1 = 'Yes'
        pat2 = 'No'
        
        if re.search(pat1, resp) is not None:
            return filt_df['Yes'].values[0]
        elif re.search(pat2, resp) is not None:
            return filt_df['No'].values[0]
        else:
            return filt_df["Don't Know"].values[0]
    
    elif txt == 'Does the applicant gets breathless when trying to keep up with others on level ground?':
        pat1 = 'Yes'
        pat2 = 'No'
        
        if re.search(pat1, resp) is not None:
            return filt_df['Yes'].values[0]
        elif re.search(pat2, resp) is not None:
            return filt_df['No'].values[0]
        else:
            return filt_df["Don't Know"].values[0]
    
    elif txt == 'Does the applicant gets breathless when walking on level ground at his pace?':
        pat1 = 'Yes'
        pat2 = 'No'
        
        if re.search(pat1, resp) is not None:
            return filt_df['Yes'].values[0]
        elif re.search(pat2, resp) is not None:
            return filt_df['No'].values[0]
        else:
            return filt_df["Don't Know"].values[0]
    
    elif txt == 'Does the applicant gets breathless when getting dressed or trying to leave his home?':
        pat1 = 'Yes'
        pat2 = 'No'
        
        if re.search(pat1, resp) is not None:
            return filt_df['Yes'].values[0]
        elif re.search(pat2, resp) is not None:
            return filt_df['No'].values[0]
        else:
            return filt_df["Don't Know"].values[0]


@app.post('/extract-text')
def extract_text():
    file = request.files['file']
    if file:
        # file.save(f'assets/{secure_filename(file.filename)}')
        extracted_text = extract_text_from_pdf(file)
        session['extracted_text'] = extracted_text 
        return {"status": 'success', "message": 'File uploaded successfully', "extracted_text": extracted_text}
    return {"status": 'error', "message": 'File not valid'}
    # return render_template('index.html', extracted_text=extracted_text)


@app.get('/analyze-pdf')
def analyze_text():
    extracted_text = session.get('extracted_text')

    total_marks = 0
    table_data = []
    question_counter = 0
    
    if extracted_text:
        chunks = chunk_text(extracted_text)
        docs = process_pdf_with_semantic_chunking(extracted_text)


        for question, marks in qs_list:
                
            if question == 'Permanent disability or condition (expected not to improve for at least 3 years)?':
                prompt2 = f'''I will give you a document and a question. Based on the document, provide me
                an answer to the question.You must answer in the following words:
                1. Yes
                2. No
                You are not allowed to respond with anything else.
                
                [start of question]
                {question}
                [end of question]

                [start of document]
                {chunks["Walking ability"]}
                {docs}
                    [end of document]
                    Remember, you cannot respond with anything other than "Yes" or "No".

                    Example 1: 
                    Description of conditions:
                    Autoimmune Cirrhosis causing chronic fatigue, some days he is unable to go out,
                    because of the fatigue.
                    
                    Answer: Yes

                    Example 2: 
                    Description of conditions:
                    Atrial Fibrilation
                    Painful knees and ankle
                    
                    Answer: Yes

                    Example 3: 
                    Description of conditions:
                    Charles suffered an ischemic stroke on 14.07.2023 and has left sided paralysis (arm and leg) and hemianopia (left sided vision loss). He is in a rehab centre and has started to walk a few metres with the support of 2 physiotherapists and a quad walking stick. He will need the use of a wheelchair outside the home/rehab environment.
                    Although he is likely to be in the rehab centre until February 2024, we shall start to have day trips to shopping centres and restaurants hence the need for a blue badge at this point.
                    
                    Answer: Yes

                    Example 4:
                    Description of conditions:
                    She has extensive osteoarthritis across her body which has already resulted in a left knee replacement and on her right side is affecting her R shoulder and R knee and awaits Knee replacement surgery to be carried out at some point. Has persistent problems with shoulder Spurs which despite recent operation still cause a huge amount of pain in that region and lack of use of the arm.
                    These issues have affected both the mobility and flexibility considerably.
                    Mrs H has previously had cancer in the brain which she has come through although as a consequence is completely deaf in one ear and it's very poor in the other leaving her feeling vulnerable. She also has other medical issues which cause her a lot of stress and anxiety particularly IBS which has taken away her confidence when she is out and about which have potentially been the triggers for a number of recent TIAs.
                    
                    Answer: Yes

                    Example 5:
                    Description of conditions:
                    W suffers from bilateral osteoarthritis of the knees with X-ray showing KL Grade 4 osteoarthritis bilaterally.
                    In particular, she suffer from osteoarthritis in the inner part of both knee joints (worse in the right knee) and early-stage osteoarthritis in the outer part of both knee joints.
                    
                    Answer: Yes

                    If the {chunks["Walking ability"]} OR  {docs} states that the person has 'Aortic/aortic abdominal aneurism', 'Atrial fibrillation/irregular heartbeat', 'Bypass/other heart surgery',
                    'Chest pain/angina','Congenital heart disease','Endocarditis','Peripheral arterial/vascular disease','Brittle Asthma','Bronchitis','Bronchiectasis',
                    'Chronic Obstructive Pulmonary Disease (COPD)Emphysema/chronic bronchitis', 'Cystic fibrosis','pneumoconiosis', 'asbestosis','silicosis','Idiopathic pulmonary fibrosis',
                    'Lung cancer','Ataxia (acute or hereditary)','Cerebral Palsy','Cerebral Vascular Disease(CVA)','Corticobasal degeneration','Head injury /Hydrocephalus','Hemiplegia',
                    'Huntington’s disease','Motor Neurone Disease(MND)','Multiple Sclerosis (M.S)'Meniere’s Disease','Myaesthenia Gravis','Myotonic/Muscular Dystrophy','Parkinson’s Disease',
                    'Peripheral Neuropathy','Progressive Supranuclear Palsy (PSP)','Stroke','Gout',
                    'Osteoarthritis','Rheumatoid arthritis','Diabetes','Terminal illness and cancer with secondary malignancies/metastasises',
                    'Chronic Kidney Failure (CKD)','Fibromyalgia','Congenital bone deformities', then the answer for this {question} should be 'Yes'.
                '''
                response = yes_no_unsure(prompt2)
                score_value = score_different(question, response, df)
                total_marks += score_value
                table_data.append([question, marks, response, score_value])
                question_counter += 1
                
            
            elif question == 'Do your health conditions affect your walking all the time?':
                prompt2 = f'''I will give you a document and a question. Based on the document, provide me
                an answer to the question.You must answer in the following words:
                1. Yes
                2. No
                You are not allowed to respond with anything else.
                
                [start of question]
                {question}
                [end of question]

                [start of document]
                {chunks["Balance, coordination or posture"]}
                {docs}
                    [end of document]
                    Remember, you cannot respond with anything other than "Yes" or "No".

                    Example 1:
                    How often does condition affect walking?
                    Always
                    Answer: Yes

                    Example 2:
                    How often does condition affect walking?
                    Sometimes
                    Answer: No


                    Example 3:
                    How often does condition affect walking?
                    Never
                    Answer: No
                    
                    '''
                response = yes_no_unsure(prompt2)
                score_value = score_different(question, response, df)
                total_marks += score_value
                table_data.append([question, marks, response, score_value])
                question_counter += 1
                # progress_bar_1.progress(question_counter / 6)
                


            elif question == 'Have you seen a healthcare professional for any falls in the last 12 months?':
                prompt2 = f'''I will give you a document and a question. Based on the document, provide me
                an answer to the question.You must answer in the following words:
                1. Yes
                2. No
                You are not allowed to respond with anything else.
                
                [start of question]
                {question}
                [end of question]

                [start of document]
                {chunks["Balance, coordination or posture"]}
                {docs}
                    [end of document]
                    Remember, you cannot respond with anything other than "Yes" or "No".

                    Example 1: 
                    Seen HCP for falls in last 12 months: No
                    Answer: NO

                    Example 2:
                    Seen HCP for falls in last 12 months: Yes
                    Answer: Yes

                '''
                response = yes_no_unsure(prompt2)
                score_value = score_different(question, response, df)
                total_marks += score_value
                table_data.append([question, marks, response, score_value])
                question_counter+=1
                # progress_bar_1.progress(question_counter / 6)
                
            
            elif question == 'For how long can the applicant walk?':
                prompt1 = f'''I will give you a document and a question. Based on the document, provide me
                an answer to the question. You must answer in the following words:
                1. Can't walk
                2. <1 min
                3. 1-5 mins
                4. 5-10 mins
                5. >10 mins
                You are not allowed to respond with anything else.
            
                
                [start of question]
                {question}
                [end of question]

                [start of document]
                {chunks["Walking ability"]}
                {docs}
                    [end of document]
                
                Example 1:
                How long it takes:3 or 4 minutes
                Answer: 1-5 minutes

                Example 2:
                How long it takes:3 minutes
                Answer: 1-5 minutes

                Example 3:
                How long it takes:4 Mins
                Answer: 1-5 minutes

                Example 4:
                How long it takes:10-15 min
                Answer:>10 mins

                Example 5:
                How long it takes:15 minutes
                Answer:>10 mins

                Example 6:
                How long it takes:Only very short distances so a minute or so because of inability to go further
                Answer: <1 min

                Example 7:
                How long it takes: 20 minutes?
                Answer:>10 mins

                Example 8:
                How long it takes:5 minutes
                Answer: 1-5 mins
                '''
                response = yes_no_unsure(prompt1)
                score_value = score_different(question, response, df)
                total_marks += score_value
                table_data.append([question, marks, response, score_value])
                question_counter+=1
                # progress_bar_1.progress(question_counter / 6)
                

            elif question == 'How far is the applicant able to walk? ':
                prompt2 = f'''I will give you a document and a question. Based on the document, provide me
                an answer to the question.You must answer in the following words:
                1. <30 m
                2. <80 m
                3. >80 m
                4. Don't Know
                
                You are not allowed to respond with anything else.
                
                [start of question]
                {question}
                [end of question]

                [start of document]
                {chunks["Walking ability"]}
                
                    [end of document]
                
                Remember, you cannot respond with anything other than "<30 m", "<80 m", ">80 m" or "Don't Know".
                If the nothing related to 'How far is the applicant able to walk?' is explicitly mentioned in the {chunks["Walking ability"]}, then answer it only as "Don't Know".
                If the person cannot walk at all or can only walk indoors, the answer should be "<30 m".
                If the person can walk outdoors but only a few blocks or near the person's house, the answer should be "<80 m".                    
                If the person can walk outdoors, on streets and roads, from one place to another, the answer should be ">80 m".

                Example 1: 
                From my home to junction Victoria Quadrant and Worthy Lane
                Answer: >80 m

                Example 2:
                He has started to walk a few metres with the support of 2 physiotherapists and a quad walking stick. He will need the use of a wheelchair outside the home/rehab environment.
                Answer: <30 m

                Example 3:
                She can walk about 50 m before needing to stop because of the pain.
                Answer: <80 m

                Example 4:
                From home to the Co Op on Portishead Marina. Needs to stop on the way.
                Answer: >80 m

                Example 5:
                From our home to end of street,which is 3 bungalows.
                Answer: >80 m

                Example 6:
                I can walk from the entrance of my home 56 Church Lane Hutton, Weston Super Mare past the primary school to the third cottage along the main road.
                Answer: >80 m

                Example 7:
                From my house number 14 to start of road 2, approximately 7 houses.
                Answer: <80 m

                Example 8:
                From my home, along the High Street to Boots.
                Answer: >80 m

                Example 9:
                In a great deal of discomfort when walking even short distances was dropped off behind our premises at 65 High St adjacent to the Station Road car park Nailsea. 
                She can walk about 50 m before needing to stop because of the pain.
                Answer: <80 m

                Example 10:
                In his walking test he managed 260 meters in six minutes but that was on a good day and he was pushing himself to make a good impression.
                Answer: >80m
                '''
                response = yes_no_unsure(prompt2)
                score_value = score_different(question, response, df)
                total_marks += score_value
                table_data.append([question, marks, response, score_value])
                question_counter += 1
                # progress_bar_1.progress(question_counter / 6)
            
        
                
            
            elif question == 'Do you have help to get around?':
                prompt2 = f'''I will give you a document and a question. Based on the document, provide me
                an answer to the question.You must answer in the following words:
                1. Yes
                2. No
                3. Don't Know
                You are not allowed to respond with anything else.
                
                [start of question]
                {question}
                [end of question]

                [start of document]
                {chunks["Balance and coordination - further details"]}
                {docs}
                    [end of document]

                    Example 1: 
                Mobility aids:
                    Quad stick, Prescribed by a healthcare professional, Just for practising in rehab. Likely will use this in the home environment upon discharge.
                    Wheelchair, Prescribed by a healthcare professional, Everything at the moment and expected to be used at all times outside.
                    Answer: Yes

                    Example 2:
                    Mobility aids
                    Raised Furniture, Bought privately, Difficulty standing from a seated position as stated before. Also use it for support when moving around the home.
                    Raised toilet seat, Bought privately, Has problems mobilising upwards.
                    Grab rails, Prescribed by a healthcare professional, Fitted rails for the stairs although needs support coming downstairs. In the shower room again needs assistance getting in and out of shower.
                    Walking stick, Bought privately, When walking about outside
                    Husband, It's a person, rather than a mobility aid, When walking about outside
                    Answer: Yes

                    Example 3:
                    Mobility aids
                    Private vehicle, Bought privately, To facilitate her transportation to the places she needs to visit
                    Member of our family, It's a person, rather than a mobility aid, The family member assists them when going anywhere outside the home, provides aid when pain strikes by offering a supporting hand for walking, and helps locate a place to take immediate rest when needed.
                    Answer: Yes

                '''
                response = yes_no_unsure(prompt2)
                score_value = score_different(question, response, df)
                table_data.append([question, marks, response, score_value])
                total_marks += score_value
                question_counter += 1
                session['question_counter'] = question_counter
                session['total_marks'] = total_marks


        result_df = pd.DataFrame(table_data, columns=["Question", "Full Marks", "Answer", "Score"])
        result_df.drop(labels="Full Marks", axis=1, inplace=True)

        if(total_marks<40):
            rejected_sections = result_df[result_df['Score'] == 0]
            if not rejected_sections.empty:
                rejection_prompt = f'''I want you to summarize all the reasons for rejections:{rejected_sections}
            into a single summarized paragraph which states all the possible reasons for which the applicant was 
            refused the blue badge. Keep the summary simple and to the point so that the agent can understand it easily.'''
                reason = generate_reasons_for_rejection(rejection_prompt)
                df_json = result_df.to_json(orient='records')
                return jsonify({'data': df_json, "status": "failed", "reason": reason})   
        else:
            df_json = result_df.to_json(orient='records')
            return jsonify({'data': df_json, "status": "passed"})       
        
@app.get('/check-round-two')
def check_for_round_two():
    extracted_text = session.get('extracted_text')

    total_marks = 0
    table_data = []
    
    if extracted_text:
        chunks = chunk_text(extracted_text)
        docs = process_pdf_with_semantic_chunking(extracted_text)
        question_counter = int(session.get('question_counter'))
        total_marks = float(session.get('total_marks'))


        if question_counter >= 5 and total_marks >= 40:
                remaining_questions = qs_list[question_counter:]
                # print(remaining_questions)
                remaining_table_data = []
                # progress_bar_2 = st.progress(0)
                # progress_bar_2 = st.empty()
                for question, marks in remaining_questions:

                    if question == 'Is the way you walk or your posture affected by your condition?':
                        prompt = f'''I will give you a document and a question. Based on the document, you must answer a question. 
                            You can only answer the question with three responses:
                            1. Yes
                            2. No
                            3. Don't Know
                            
                            You are not allowed to respond with anything else.

                            [start of question]
                            {question}
                            [end of question]

                            [start of document]
                            {chunks["Walking ability"]}
                            {docs}
                            [end of document]

                            Remember, you cannot respond with anything other than "Yes", "No" or "Don't Know".
                            If the {chunks["Walking ability"]} or {docs}doesn't have any information asked in the question, then
                            kindly answer it as "Don't know" only. Answer it only as "Yes" or "No" only and only if the 
                            {chunks["Walking ability"]} or {docs} has an answer with respect to the question.

                            Example 1: 
                            Is the way you walk or your posture affected by your condition?
                            Essential I use a walking stick at all times to maintain my balance and to keep balance when a knee or ankle goes.
                            Answer:Yes

                            Example 2: 
                            Is the way you walk or your posture affected by your condition?
                            Balance, coordination or posture:shorter steps than usual, and sometimes find my self shuffling along. 
                            Have to be aware of kerbs and uneven pavements. Find myself bent over like an old man (well I suppose I am an old man now)
                            Answer:Yes

                            Example 3: 
                            Is the way you walk or your posture affected by your condition?
                            Balance, coordination or posture:No control over bottom part of left leg (below knee) due to paralysis.
                            Answer:Yes
                            '''
                        response = yes_no_unsure(prompt)
                        score_value = score(question, response, df)
                    
                        remaining_table_data.append([question, marks, response, score_value])
                        total_marks += score_value

                        # progress_bar_2.progress((question_counter + len(remaining_table_data)) / len(qs_list))

                    elif question == 'The applicant can walk around a supermarket, with the support of a trolley':
                        prompt = f'''I will give you a document and a question. Based on the document, you must answer a question. 
                            You can only answer the question with three responses:
                            1. Yes
                            2. No
                            3. Don't Know
                            
                            You are not allowed to respond with anything else.

                            [start of question]
                            {question}
                            [end of question]

                            [start of document]
                            {chunks['Balance and coordination - further details']}
                            {docs}
                            [end of document]

                            Remember, you cannot respond with anything other than "Yes", "No" or "Don't Know".
                            If the {chunks['Balance and coordination - further details']} or {docs}doesn't have any information asked in the question, then
                            kindly answer it as "Don't know" only. Answer it only as "Yes" or "No" only and only if the 
                            {chunks['Balance and coordination - further details']} or {docs}has an answer with respect to the question.

                            Example 1: 
                            Can walk around a supermarket, with the support of a trolley
                            Answer:Yes

                            Example 2: 
                            Cannot walk around a supermarket, with the support of a trolley
                            Answer:No 

                            Example 3: 
                            Can walk around a supermarket, with the support of a trolley: Mum can only walk around a supermarket if I am with her and she is using her walking frame or stick. 
                            She doesn’t have good special awareness.
                            Answer:Yes'''

                        response = yes_no_unsure(prompt)
                        score_value = score(question, response, df)
                    
                        remaining_table_data.append([question, marks, response, score_value])
                        total_marks += score_value or 0

                        # progress_bar_2.progress((question_counter + len(remaining_table_data)) / len(qs_list))

                    elif question == 'The applicant can walk up/down a single flight of stairs in a house':
                        prompt = f'''I will give you a document and a question. Based on the document, you must answer a question. 
                            You can only answer the question with three responses:
                            1. Yes
                            2. No
                            3. Don't Know
                            
                            You are not allowed to respond with anything else.

                            [start of question]
                            {question}
                            [end of question]

                            [start of document]
                            {chunks['Balance and coordination - further details']}
                            {docs}
                            [end of document]

                            Remember, you cannot respond with anything other than "Yes", "No" or "Don't Know".
                            If the {chunks['Balance and coordination - further details']} or {docs} doesn't have any information asked in the question, then
                            kindly answer it as "Don't know" only. Answer it only as "Yes" or "No" only and only if the 
                            {chunks['Balance and coordination - further details']} or {docs} has an answer with respect to the question.

                            Example 1: 
                            Can walk up/down a single flight of stairs in a house: Need supervision coming downstairs because of balance issues.
                            Answer:Yes

                            Example 2: 
                            Can only walk around 5 metres with the support of 2 physiotherapists. 
                            Although this is likely to improve, he will still find walking difficult due to paralysis of the left leg and core and will need a wheelchair for any distance.
                            Answer: No 
                            '''

                        response = yes_no_unsure(prompt)
                        score_value = score(question, response, df)
                    
                        remaining_table_data.append([question, marks, response, score_value])
                        total_marks += score_value or 0

                        # progress_bar_2.progress((question_counter + len(remaining_table_data)) / len(qs_list))
                    
                    elif question == 'The applicant can only walk around indoors':
                        prompt = f'''I will give you a document and a question. Based on the document, you must answer a question. 
                            You can only answer the question with three responses:
                            1. Yes
                            2. No
                            3. Don't Know
                            
                            You are not allowed to respond with anything else.

                            [start of question]
                            {question}
                            [end of question]

                            [start of document]
                            {extracted_text}
                            {docs}
                            [end of document]

                            Remember, you cannot respond with anything other than "Yes", "No" or "Don't Know".
                            If the {extracted_text} doesn't have any information asked in the question, then
                            kindly answer it as "Don't know" only. Answer it only as "Yes" or "No" only and only if the 
                            {extracted_text} has an answer with respect to the question.
                            '''

                        response = yes_no_unsure(prompt)
                        score_value = score(question, response, df)
                    
                        remaining_table_data.append([question, marks, response, score_value])
                        total_marks += score_value or 0

                        # progress_bar_2.progress((question_counter + len(remaining_table_data)) / len(qs_list))
                    
                    elif question == 'The applicant can walk around a small shopping centre':
                        prompt = f'''I will give you a document and a question. Based on the document, you must answer a question. 
                            You can only answer the question with three responses:
                            1. Yes
                            2. No
                            3. Don't Know
                            
                            You are not allowed to respond with anything else.

                            [start of question]
                            {question}
                            [end of question]

                            [start of document]
                            {chunks['Balance and coordination - further details']}
                            {docs}
                            [end of document]

                            Remember, you cannot respond with anything other than "Yes", "No" or "Don't Know".
                            If the {chunks['Balance and coordination - further details']} or {docs} doesn't have any information asked in the question, then
                            kindly answer it as "Don't know" only. Answer it only as "Yes" or "No" only and only if the 
                            {chunks['Balance and coordination - further details']} or {docs} has an answer with respect to the question.
                            '''

                        response = yes_no_unsure(prompt)
                        score_value = score(question, response, df)
                    
                        remaining_table_data.append([question, marks, response, score_value])
                        total_marks += score_value or 0

                        # progress_bar_2.progress((question_counter + len(remaining_table_data)) / len(qs_list))
                    
                    elif question == 'Does the applicant require pain medication':
                        prompt = f'''I will give you a document and a question. Based on the document, you must answer a question. 
                            You can only answer the question with three responses:
                            1. Yes
                            2. No
                            3. Don't Know
                            
                            You are not allowed to respond with anything else.

                            [start of question]
                            {question}
                            [end of question]

                            [start of document]
                            {chunks["Walking ability"]}
                            {docs}
                            [end of document]

                            Remember, you cannot respond with anything other than "Yes", "No" or "Don't Know".
                            If the {chunks["Walking ability"]} or {docs} doesn't have any information asked in the question, then
                            kindly answer it as "Don't know" only. Answer it only as "Yes" or "No" only and only if the 
                            {chunks["Walking ability"]} or {docs} has an answer with respect to the question.
                            '''

                        response = yes_no_unsure(prompt)
                        score_value = score(question, response, df)
                    
                        remaining_table_data.append([question, marks, response, score_value])
                        total_marks += score_value or 0

                        # progress_bar_2.progress((question_counter + len(remaining_table_data)) / len(qs_list))
                    
                    elif question == 'When the applicant takes pain relief medication they can cope with the pain':
                        prompt = f'''I will give you a document and a question. Based on the document, you must answer a question. 
                            You can only answer the question with three responses:
                            1. Yes
                            2. No
                            3. Don't Know
                            
                            You are not allowed to respond with anything else.

                            [start of question]
                            {question}
                            [end of question]

                            [start of document]
                            {chunks["Walking ability"]}
                            {docs}
                            [end of document]

                            Remember, you cannot respond with anything other than "Yes", "No" or "Don't Know".
                            If the {chunks["Walking ability"]} or {docs} doesn't have any information asked in the question, then
                            kindly answer it as "Don't know" only. Answer it only as "Yes" or "No" only and only if the 
                            {chunks["Walking ability"]} or {docs} has an answer with respect to the question.

                            Example 1:
                            Excessive pain - further details
                            Uses pain relief medication
                            Have to stop and take regular breaks: The pain in my lower back, spine and supporting muscles gets so bad that 
                            I can't walk and have to sit down until it abates enough to stand up again. My legs shake and they ache which makes 
                            it hard to keep standing let alone walk.
                            Answer: No

                            Example 2:
                            Excessive pain - further details
                            Uses pain relief medication
                            Answer: Yes
                            
                            Example 3:
                            Uses pain relief medication
                            
                            '''

                        response = yes_no_unsure(prompt)
                        score_value = score(question, response, df)
                    
                        remaining_table_data.append([question, marks, response, score_value])
                        total_marks += score_value or 0

                        # progress_bar_2.progress((question_counter + len(remaining_table_data)) / len(qs_list))
                    
                    elif question == 'Even after taking pain relief medication the pain makes the applicant physically sick':
                        prompt = f'''I will give you a document and a question. Based on the document, you must answer a question. 
                            You can only answer the question with three responses:
                            1. Yes
                            2. No
                            3. Don't Know
                            
                            You are not allowed to respond with anything else.

                            [start of question]
                            {question}
                            [end of question]

                            [start of document]
                            {chunks["Walking ability"]}
                            {docs}
                            [end of document]

                            Remember, you cannot respond with anything other than "Yes", "No" or "Don't Know".
                            If the {chunks["Walking ability"]} or {docs} doesn't have any information asked in the question, then
                            kindly answer it as "Don't know" only. Answer it only as "Yes" or "No" only and only if the 
                            {chunks["Walking ability"]} or {docs} has an answer with respect to the question.
                            '''

                        response = yes_no_unsure(prompt)
                        score_value = score(question, response, df)
                    
                        remaining_table_data.append([question, marks, response, score_value])
                        total_marks += score_value or 0

                        # progress_bar_2.progress((question_counter + len(remaining_table_data)) / len(qs_list))
                    
                    elif question == 'Even after taking pain relief medication is frequently in so much pain that walking for more than 2 minutes is unbearable':
                        prompt = f'''I will give you a document and a question. Based on the document, you must answer a question. 
                            You can only answer the question with three responses:
                            1. Yes
                            2. No
                            3. Don't Know
                            
                            You are not allowed to respond with anything else.

                            [start of question]
                            {question}
                            [end of question]

                            [start of document]
                            {chunks["Walking ability"]}
                            {docs}
                            [end of document]

                            Remember, you cannot respond with anything other than "Yes", "No" or "Don't Know".
                            If the {chunks["Walking ability"]}or {docs} doesn't have any information asked in the question, then
                            kindly answer it as "Don't know" only. Answer it only as "Yes" or "No" only and only if the 
                            {chunks["Walking ability"]} or {docs} has an answer with respect to the question.

                            Example: Frequently in so much pain that walking for more than 2 minutes is unbearable: The individual experiences intermittent pain that occurs at unpredictable times (daily). 
                            When the pain strikes, it is severe enough that they cannot continue walking for more than 2 minutes without needing immediate rest/ regular break. 
                            This pain disrupts their ability to walk comfortably and can occur suddenly, making it challenging to predict when they will need to stop and rest.
                            Answer: Yes

                            Example: When the pain strikes, it is severe enough that they cannot continue walking for more than 2 minutes without needing immediate rest/ regular break. 
                            This pain disrupts their ability to walk comfortably and can occur suddenly, making it challenging to predict when they will need to stop and rest.
                            Answer: Yes
                            '''

                        response = yes_no_unsure(prompt)
                        score_value = score(question, response, df)
                    
                        remaining_table_data.append([question, marks, response, score_value])
                        total_marks += score_value or 0

                        # progress_bar_2.progress((question_counter + len(remaining_table_data)) / len(qs_list))
                    
                    elif question == 'Does the applicant gets breathless when walking up a slight hill?':
                        prompt = f'''I will give you a document and a question. Based on the document, you must answer a question. 
                            You can only answer the question with three responses:
                            1. Yes
                            2. No
                            3. Don't Know
                            
                            You are not allowed to respond with anything else.

                            [start of question]
                            {question}
                            [end of question]

                            [start of document]
                            {chunks["When they get breathless"]}
                            {docs}
                            [end of document]

                            Remember, you cannot respond with anything other than "Yes", "No" or "Don't Know".
                            If the {chunks["When they get breathless"]} or {docs} doesn't have any information asked in the question, then
                            kindly answer it as "Don't know" only. Answer it only as "Yes" or "No" only and only if the 
                            {chunks["When they get breathless"]} or {docs} has an answer with respect to the question.

                            Example: 
                            When they get breathless
                             Getting dressed or trying to leave my home, Trying to keep up with others on level ground, 
                             Walking on level ground at my own pace, Walking up a slight hill.
                             Answer: Yes

                             Example: 
                            When they get breathless
                             Getting dressed or trying to leave my home, Trying to keep up with others on level ground, 
                             Walking on level ground at my own pace, Walking up a slight hill.
                             Answer: Yes

                             Example: 
                            When they get breathless
                             Getting dressed or trying to leave my home, Trying to keep up with others on level ground, 
                             Walking on level ground at my own pace, Walking up a slight hill.
                             Answer: Yes
                            '''

                        response = yes_no_unsure(prompt)
                        score_value = score(question, response, df)
                    
                        remaining_table_data.append([question, marks, response, score_value])
                        total_marks += score_value or 0

                        # progress_bar_2.progress((question_counter + len(remaining_table_data)) / len(qs_list))
                    
                    elif question == 'Does the applicant gets breathless when trying to keep up with others on level ground?':
                        prompt = f'''I will give you a document and a question. Based on the document, you must answer a question. 
                            You can only answer the question with three responses:
                            1. Yes
                            2. No
                            3. Don't Know
                            
                            You are not allowed to respond with anything else.

                            [start of question]
                            {question}
                            [end of question]

                            [start of document]
                            {chunks["When they get breathless"]}
                            {docs}
                            [end of document]

                            Remember, you cannot respond with anything other than "Yes", "No" or "Don't Know".
                            If the {chunks["When they get breathless"]} or {docs} doesn't have any information asked in the question, then
                            kindly answer it as "Don't know" only. Answer it only as "Yes" or "No" only and only if the 
                            {chunks["When they get breathless"]} or {docs} has an answer with respect to the question.

                            Example: 
                            When they get breathless
                             Getting dressed or trying to leave my home, Trying to keep up with others on level ground, 
                             Walking on level ground at my own pace, Walking up a slight hill.
                             Answer: Yes

                             Example: 
                            When they get breathless
                             Getting dressed or trying to leave my home, Trying to keep up with others on level ground, 
                             Walking on level ground at my own pace, Walking up a slight hill.
                             Answer: Yes

                             Example: 
                            When they get breathless
                             Getting dressed or trying to leave my home, Trying to keep up with others on level ground, 
                             Walking on level ground at my own pace, Walking up a slight hill.
                             Answer: Yes
                            '''

                        response = yes_no_unsure(prompt)
                        score_value = score(question, response, df)
                    
                        remaining_table_data.append([question, marks, response, score_value])
                        total_marks += score_value or 0

                        # progress_bar_2.progress((question_counter + len(remaining_table_data)) / len(qs_list))
                    
                    elif question == 'Does the applicant gets breathless when walking on level ground at his pace?':
                        prompt = f'''I will give you a document and a question. Based on the document, you must answer a question. 
                            You can only answer the question with three responses:
                            1. Yes
                            2. No
                            3. Don't Know
                            
                            You are not allowed to respond with anything else.

                            [start of question]
                            {question}
                            [end of question]

                            [start of document]
                            {chunks["When they get breathless"]}
                            {docs}
                            [end of document]

                            Remember, you cannot respond with anything other than "Yes", "No" or "Don't Know".
                            If the {chunks["When they get breathless"]} or {docs}doesn't have any information asked in the question, then
                            kindly answer it as "Don't know" only. Answer it only as "Yes" or "No" only and only if the 
                            {chunks["When they get breathless"]} or {docs} has an answer with respect to the question.

                            Example: 
                            When they get breathless
                             Getting dressed or trying to leave my home, Trying to keep up with others on level ground, 
                             Walking on level ground at my own pace, Walking up a slight hill.
                             Answer: Yes

                             Example: 
                            When they get breathless
                             Getting dressed or trying to leave my home, Trying to keep up with others on level ground, 
                             Walking on level ground at my own pace, Walking up a slight hill.
                             Answer: Yes

                             Example: 
                            When they get breathless
                             Getting dressed or trying to leave my home, Trying to keep up with others on level ground, 
                             Walking on level ground at my own pace, Walking up a slight hill.
                             Answer: Yes
                            '''

                        response = yes_no_unsure(prompt)
                        score_value = score(question, response, df)
                    
                        remaining_table_data.append([question, marks, response, score_value])
                        total_marks += score_value or 0

                        # progress_bar_2.progress((question_counter + len(remaining_table_data)) / len(qs_list))
                            
                    elif question == 'Does the applicant gets breathless when getting dressed or trying to leave his home?':
                        prompt = f'''I will give you a document and a question. Based on the document, you must answer a question. 
                            You can only answer the question with three responses:
                            1. Yes
                            2. No
                            3. Don't Know
                            
                            You are not allowed to respond with anything else.

                            [start of question]
                            {question}
                            [end of question]

                            [start of document]
                            {chunks["When they get breathless"]}
                            {docs}
                            [end of document]

                            Remember, you cannot respond with anything other than "Yes", "No" or "Don't Know".
                            If the {chunks["When they get breathless"]} or {docs} doesn't have any information asked in the question, then
                            kindly answer it as "Don't know" only. Answer it only as "Yes" or "No" only and only if the 
                            {chunks["When they get breathless"]} or {docs} has an answer with respect to the question.

                            Example: 
                            When they get breathless
                             Getting dressed or trying to leave my home, Trying to keep up with others on level ground, 
                             Walking on level ground at my own pace, Walking up a slight hill.
                             Answer: Yes

                             Example: 
                            When they get breathless
                             Getting dressed or trying to leave my home, Trying to keep up with others on level ground, 
                             Walking on level ground at my own pace, Walking up a slight hill.
                             Answer: Yes

                             Example: 
                            When they get breathless
                             Getting dressed or trying to leave my home, Trying to keep up with others on level ground, 
                             Walking on level ground at my own pace, Walking up a slight hill.
                             Answer: Yes
                            '''

                        response = yes_no_unsure(prompt)
                        score_value = score(question, response, df)
                    
                        remaining_table_data.append([question, marks, response, score_value])
                        total_marks += score_value or 0

                remaining_result_df = pd.DataFrame(remaining_table_data, columns=["Question", "Full Marks", "Answer", "Score"])
                remaining_result_df.drop(labels="Full Marks", axis=1, inplace=True)

                df_json = remaining_result_df.to_json(orient='records')

                if(total_marks<60):
                    rejected_sections = remaining_result_df[remaining_result_df['Score'] == 0]
                    if not rejected_sections.empty:
                        rejection_prompt = f'''I want you to summarize all the reasons for rejections:{rejected_sections}
                    into a single summarized paragraph which states all the possible reasons for which the applicant was 
                    refused the blue badge. Keep the summary simple and to the point so that the agent can understand it easily.'''
                        reason = generate_reasons_for_rejection(rejection_prompt)
                        df_json = remaining_result_df.to_json(orient='records')
                        return jsonify({'data': df_json, "status": "failed", "reason": reason,"total_score": total_marks})
                    # return jsonify({'data': df_json, "status": "failed","total_score": total_marks})   
                else:
                    df_json = remaining_result_df.to_json(orient='records')
                    return jsonify({'data': df_json, "status": "passed","total_score": total_marks})     
    
                        # progress_bar_2.progress((question_counter + len(remaining_table_data)) / len(qs_list))

                            
            # Display the table of questions, answers, and marks for the first 5 questions
                # st.subheader("Assessment Results")
                # remaining_result_df = pd.DataFrame(remaining_table_data, columns=["Question", "Full Marks", "Answer", "Score"])
                # remaining_result_df.drop(labels="Full Marks", axis=1, inplace=True)
                # st.dataframe(remaining_result_df)

                # st.subheader("Total Marks")
                # st.write("# **", total_marks, "**")  # Use double asterisks for bold and bigger font
                # if total_marks >= 60:
                #     st.success("Passed - Agent should issue the Blue Badge")
                # elif 40 <= total_marks < 60:
                #     st.success('Team analysis required')
                # else:
                #     st.error("Failed")
                