SCORING_PROMPT = '''
    **start of instructions**
    I will give you a document and a question. Based on the document, provide me
    an answer to the question.You must answer in the following words:
        **start of options**
        {options}
        **end of options**
    You are not allowed to respond with anything else.
    **end of instructions**
    
    Remember, you cannot respond with anything other than {options}.
    For quantitative responses, choose the highest value that can be inferred.
    
    **start of question**
    {question}
    **end of question**
    
    **start of document**
    {docs}
    **end of document**
    
    **start of examples**
    {examples}
    **end of examples**
    
    **start of notes**
    {notes}
    **end of notes**

'''

REJECTION_PROMPT = '''I want you to summarize all the reasons for rejections in the given segments
into a single summarized paragraph which states all the possible reasons for which the applicant was
refused the blue badge. Keep the summary simple and to the point so that the agent can understand it easily.
**start of segments**
{segments}
**end of segments**
'''
