part_one = {
    'questions': {
        'Permanent disability or condition (expected not to improve for at least 3 years)?': {
            'options': {
                'Yes': 1,
                'No': 0
            },
            'max_marks': 1,
            'examples': {
                'Example 1': {
                    'condition': [
                        "Autoimmune Cirrhosis causing chronic fatigue, some days he is unable to go out, because of"
                        "the fatigue."
                    ],
                    'answer': "Yes",
                },
                'Example 2': {
                    'condition': [
                        "Atrial Fibrillation",
                        "Painful knees and ankle"
                    ],
                    'answer': "Yes",
                },
                'Example 3': {
                    'condition': [
                        "Charles suffered an ischemic stroke on 14.07.2023 and has left sided paralysis (arm and leg)"
                        "and hemianopia (left sided vision loss).",
                        "He is in a rehab centre and has started to walk a few metres with the support of 2 "
                        "physiotherapists and a quad walking stick.",
                        "He will need the use of a wheelchair outside the home/rehab environment.",
                        "Although he is likely to be in the rehab centre until February 2024, we shall start to have"
                        "day trips to shopping centres and restaurants hence the need for a blue badge at this point."
                    ],
                    'answer': "Yes",
                },
                'Example 4': {
                    'condition': [
                        "She has extensive osteoarthritis across her body which has already resulted in a left knee"
                        "replacement and on her right side is affecting her R shoulder and R knee and awaits Knee "
                        "replacement surgery to be carried out at some point.",
                        "Has persistent problems with shoulder Spurs which despite recent operation still cause a"
                        "huge amount of pain in that region and lack of use of the arm.",
                        "These issues have affected both the mobility and flexibility considerably.",
                        "Mrs H has previously had cancer in the brain which she has come through although as a "
                        "consequence is completely deaf in one ear and it's very poor in the other leaving her "
                        "feeling vulnerable.",
                        "She also has other medical issues which cause her a lot of stress and anxiety particularly"
                        "IBS which has taken away her confidence when she is out and about which have potentially "
                        "been the triggers for a number of recent TIAs."
                    ],
                    'answer': "Yes",
                },
                'Example 5': {
                    'condition': [
                        "W suffers from bilateral osteoarthritis of the knees with X-ray showing KL Grade 4 "
                        "osteoarthritis bilaterally.",
                        "In particular, she suffer from osteoarthritis in the inner part of both knee joints (worse "
                        "in the right knee) and early-stage osteoarthritis in the outer part of both knee joints."
                    ],
                    'answer': "Yes",
                }
            },
            'notes': '''If the [document] states that the person has 'Aortic/aortic abdominal aneurism', 
            'Atrial fibrillation/irregular heartbeat', 'Bypass/other heart surgery', 'Chest pain/angina','Congenital 
            heart disease','Endocarditis','Peripheral arterial/vascular disease','Brittle Asthma','Bronchitis',
            'Bronchiectasis', 'Chronic Obstructive Pulmonary Disease (COPD)Emphysema/chronic bronchitis', 
            'Cystic fibrosis','pneumoconiosis', 'asbestosis','silicosis','Idiopathic pulmonary fibrosis', 
            'Lung cancer','Ataxia (acute or hereditary)','Cerebral Palsy','Cerebral Vascular Disease(CVA)',
            'Corticobasal degeneration','Head injury /Hydrocephalus','Hemiplegia', 'Huntington’s disease',
            'Motor Neurone Disease(MND)','Multiple Sclerosis (M.S)'Meniere’s Disease','Myaesthenia Gravis',
            'Myotonic/Muscular Dystrophy','Parkinson’s Disease', 'Peripheral Neuropathy','Progressive Supranuclear 
            Palsy (PSP)','Stroke','Gout', 'Osteoarthritis','Rheumatoid arthritis','Diabetes','Terminal illness and 
            cancer with secondary malignancies/metastasises', 'Chronic Kidney Failure (CKD)','Fibromyalgia',
            'Congenital bone async deformities', then the answer for this [question] should be 'Yes'.'''
        },
        'Do your health conditions affect your walking all the time?': {
            'options': {
                'Yes': 5,
                'No': 0
            },
            'max_marks': 5,
            'examples': {
                'Example 1': {
                    'condition': "How often does condition affect walking?\nAlways",
                    'answer': "Yes",
                },
                'Example 2': {
                    'condition': "How often does condition affect walking?\nSometimes",
                    'answer': "No",
                },
                'Example 3': {
                    'condition': "How often does condition affect walking?\nNever",
                    'answer': "No",
                }
            },
            'notes': ''
        },
        'Have you seen a healthcare professional for any falls in the last 12 months?': {
            'options': {
                'Yes': 0,
                'No': 0
            },
            'max_marks': 0,
            'examples': {
                'Example 1': {
                    'condition': "Seen HCP for falls in last 12 months: No",
                    'answer': "NO",
                },
                'Example 2': {
                    'condition': "Seen HCP for falls in last 12 months: Yes",
                    'answer': "Yes",
                }
            },
            'notes': ''
        },
        'For how long can the applicant walk?': {
            'options': {
                "Can't walk": 40,
                '<1 min': 35,
                '1-5 mins': 20,
                '5-10 mins': 10,
                '>10 mins': 0
            },
            'max_marks': 40,
            'examples': {
                'Example 1': {
                    'condition': "How long it takes:3 or 4 minutes",
                    'answer': "1-5 minutes",
                },
                'Example 2': {
                    'condition': "How long it takes:3 minutes",
                    'answer': "1-5 minutes",
                },
                'Example 3': {
                    'condition': "How long it takes:4 Mins",
                    'answer': "1-5 minutes",
                },
                'Example 4': {
                    'condition': "How long it takes:10-15 min",
                    'answer': ">10 mins",
                },
                'Example 5': {
                    'condition': "How long it takes:15 minutes",
                    'answer': ">10 mins",
                },
                'Example 6': {
                    'condition': "How long it takes:Only very short distances so a minute or so because of inability "
                                 "to go further",
                    'answer': "<1 min",
                },
                'Example 7': {
                    'condition': "How long it takes: 20 minutes?",
                    'answer': ">10 mins",
                },
                'Example 8': {
                    'condition': "How long it takes:5 minutes",
                    'answer': "1-5 mins",
                }
            },
            'notes': ''
        },
        'How far is the applicant able to walk?': {
            'options': {
                '<30 m': 20,
                '<80 m': 15,
                '>80 m': 0,
                "Dont Know": 0
            },
            'max_marks': 20,
            'examples': {
                'Example 1': {
                    'condition': "From my home to junction Victoria Quadrant and Worthy Lane",
                    'answer': ">80 m",
                },
                'Example 2': {
                    'condition': "He has started to walk a few metres with the support of 2 physiotherapists and a "
                                 "quad walking stick. He will need the use of a wheelchair outside the home/rehab "
                                 "environment.",
                    'answer': "<30 m",
                },
                'Example 3': {
                    'condition': "She can walk about 50 m before needing to stop because of the pain.",
                    'answer': "<80 m",
                },
                'Example 4': {
                    'condition': "From home to the Co Op on Portishead Marina. Needs to stop on the way.",
                    'answer': ">80 m",
                },
                'Example 5': {
                    'condition': "From our home to end of street,which is 3 bungalows.",
                    'answer': ">80 m",
                },
                'Example 6': {
                    'condition': "I can walk from the entrance of my home 56 Church Lane Hutton, Weston Super Mare "
                                 "past the primary school to the third cottage along the main road.",
                    'answer': ">80 m",
                },
                'Example 7': {
                    'condition': "From my house number 14 to start of road 2, approximately 7 houses.",
                    'answer': "<80 m",
                },
                'Example 8': {
                    'condition': "From my home, along the High Street to Boots.",
                    'answer': ">80 m",
                },
                'Example 9': {
                    'condition': "In a great deal of discomfort when walking even short distances was dropped off "
                                 "behind our premises at 65 High St adjacent to the Station Road car park "
                                 "Nailsea.\nShe can walk about 50 m before needing to stop because of the pain.",
                    'answer': "<80 m",
                },
                'Example 10': {
                    'condition': "In his walking test he managed 260 meters in six minutes but that was on a good day "
                                 "and he was pushing himself to make a good impression.",
                    'answer': ">80m",
                }
            },
            'notes': '''
                 - If the nothing related to 'How far is the applicant able to walk?' is explicitly mentioned in the [document], then answer it only as "Dont Know".
                 - If the person cannot walk at all or can only walk indoors, the answer should be "<30 m".
                 - If the person can walk outdoors but only a few blocks or near the person's house, the answer should be "<80 m".                    
                 - If the person can walk outdoors, on streets and roads, from one place to another, the answer should be ">80 m".
            '''
        },
        'Do you have help to get around?': {
            'options': {
                'Yes': 10,
                'No': 0,
                "Dont Know": 0
            },
            'max_marks': 10,
            'examples': {
                'Example 1': {
                    'condition': "Mobility aids:\nQuad stick, Prescribed by a healthcare professional, Just for "
                                 "practising in rehab. Likely will use this in the home environment upon "
                                 "discharge.\nWheelchair, Prescribed by a healthcare professional, Everything at the "
                                 "moment and expected to be used at all times outside.",
                    'answer': "Yes",
                },
                'Example 2': {
                    'condition': "Mobility aids\nRaised Furniture, Bought privately, Difficulty standing from a "
                                 "seated position as stated before. Also use it for support when moving around the "
                                 "home.\nRaised toilet seat, Bought privately, Has problems mobilising upwards.\nGrab "
                                 "rails, Prescribed by a healthcare professional, Fitted rails for the stairs "
                                 "although needs support coming downstairs. In the shower room again needs assistance "
                                 "getting in and out of shower.\nWalking stick, Bought privately, When walking about "
                                 "outside\nHusband, It's a person, rather than a mobility aid, When walking about "
                                 "outside",
                    'answer': "Yes",
                },
                'Example 3': {
                    'condition': "Mobility aids\nPrivate vehicle, Bought privately, To facilitate her transportation "
                                 "to the places she needs to visit\nMember of our family, It's a person, rather than "
                                 "a mobility aid, The family member assists them when going anywhere outside the "
                                 "home, provides aid when pain strikes by offering a supporting hand for walking, "
                                 "and helps locate a place to take immediate rest when needed.",
                    'answer': "Yes",
                }
            },
            'notes': ''
        },
    }
}
# print(part_one['questions']['Permanent disability or condition (expected not to improve for at least 3 years)?']['examples'])

part_two = {
    'questions': {
        'Is the way you walk or your posture affected by your condition?': {
            'options': {
                'Yes': 4,
                'No': 0,
                "Dont Know": 0
            },
            'max_marks': 4,
            'examples': {
                'Example 1': {
                    'condition': "Is the way you walk or your posture affected by your condition?\nEssential I use a walking stick at all times to maintain my balance and to keep balance when a knee or ankle goes.",
                    'answer': "Yes",
                },
                'Example 2': {
                    'condition': "Is the way you walk or your posture affected by your condition?\nBalance, coordination or posture:shorter steps than usual, and sometimes find my self shuffling along.\nHave to be aware of kerbs and uneven pavements. Find myself bent over like an old man (well I suppose I am an old man now)",
                    'answer': "Yes",
                },
                'Example 3': {
                    'condition': "Is the way you walk or your posture affected by your condition?\nBalance, coordination or posture:No control over bottom part of left leg (below knee) due to paralysis.",
                    'answer': "Yes",
                }
            },
            'notes': '''
                If the [document] doesn't have any information asked in the question, then
                kindly answer it as "Dont Know" only. Answer it only as "Yes" or "No" only and only if the 
                [document] has an answer with respect to the question. Don't try to infer anything.
            '''
        },
        'The applicant can walk around a supermarket, with the support of a trolley': {
            'options': {
                'Yes': 0,
                'No': 4,
                "Dont Know": 0
            },
            'max_marks': 4,
            'examples': {
                'Example 1': {
                    'condition': "Can walk around a supermarket, with the support of a trolley",
                    'answer': "Yes",
                },
                'Example 2': {
                    'condition': "Cannot walk around a supermarket, with the support of a trolley",
                    'answer': "No",
                },
                'Example 3': {
                    'condition': "Can walk around a supermarket, with the support of a trolley: Mum can only walk around a supermarket if I am with her and she is using her walking frame or stick.\nShe doesn’t have good special awareness.",
                    'answer': "Yes",
                }
            },
            'notes': '''
                If the [document] doesn't have any information asked in the question, then
                kindly answer it as "Dont Know" only. Answer it only as "Yes" or "No" only and only if the 
                [document] has an answer with respect to the question. Don't try to infer anything.
            '''
        },
        'The applicant can walk up/down a single flight of stairs in a house': {
            'options': {
                'Yes': 0,
                'No': 4,
                "Dont Know": 0
            },
            'max_marks': 4,
            'examples': {
                'Example 1': {
                    'condition': "Can walk up/down a single flight of stairs in a house: Need supervision coming downstairs because of balance issues.",
                    'answer': "Yes",
                },
                'Example 2': {
                    'condition': "Can only walk around 5 metres with the support of 2 physiotherapists. Although this is likely to improve, he will still find walking difficult due to paralysis of the left leg and core and will need a wheelchair for any distance.",
                    'answer': "No",
                }
            },
            'notes': '''
                If the [document] doesn't have any information asked in the question, then
                kindly answer it as "Dont Know" only. Answer it only as "Yes" or "No" only and only if the 
                [document] has an answer with respect to the question. Don't try to infer anything.
            '''
        },
        'The applicant can only walk around indoors': {
            'options': {
                'Yes': 4,
                'No': 0,
                "Dont Know": 0
            },
            'max_marks': 4,
            'examples': {},
            'notes': '''
                If the [document] doesn't have any information asked in the question, then
                kindly answer it as "Dont Know" only. Answer it only as "Yes" or "No" only and only if the 
                [document] has an answer with respect to the question. Don't try to infer anything.
            '''
        },
        'The applicant can walk around a small shopping centre': {
            'options': {
                'Yes': 0,
                'No': 4,
                "Dont Know": 0
            },
            'max_marks': 4,
            'examples': {},
            'notes': '''
                If the [document] doesn't have any information asked in the question, then
                kindly answer it as "Dont Know" only. Answer it only as "Yes" or "No" only and only if the 
                [document] has an answer with respect to the question. Don't try to infer anything.
            '''
        },
        'Does the applicant require pain medication': {
            'options': {
                'Yes': 1,
                'No': 0,
                "Dont Know": 0
            },
            'max_marks': 1,
            'examples': {},
            'notes': '''
                If the [document] doesn't have any information asked in the question, then
                kindly answer it as "Dont Know" only. Answer it only as "Yes" or "No" only and only if the 
                [document] has an answer with respect to the question. Don't try to infer anything.
            '''
        },
        'When the applicant takes pain relief medication they can cope with the pain': {
            'options': {
                'Yes': 0,
                'No': 4,
                "Dont Know": 0
            },
            'max_marks': 4,
            'examples': {
                'Example 1': {
                    'condition': "Excessive pain - further details\nUses pain relief medication\nHave to stop and take regular breaks: The pain in my lower back, spine and supporting muscles gets so bad that I can't walk and have to sit down until it abates enough to stand up again. My legs shake and they ache which makes it hard to keep standing let alone walk.",
                    'answer': "No",
                },
                'Example 2': {
                    'condition': "Excessive pain - further details\nUses pain relief medication",
                    'answer': "Yes",
                }
            },
            'notes': '''
                If the [document] doesn't have any information asked in the question, then
                kindly answer it as "Dont Know" only. Answer it only as "Yes" or "No" only and only if the 
                [document] has an answer with respect to the question. Don't try to infer anything.
            '''
        },
        'Even after taking pain relief medication the applicant must stop and take regular breaks': {
            'options': {
                'Yes': 4,
                'No': 0,
                "Dont Know": 0
            },
            'max_marks': 4,
            'examples': {},
            'notes': '''
                If the [document] doesn't have any information asked in the question, then
                kindly answer it as "Dont Know" only. Answer it only as "Yes" or "No" only and only if the 
                [document] has an answer with respect to the question. Don't try to infer anything.
            '''
        },
        'Even after taking pain relief medication the pain makes the applicant physically sick': {
            'options': {
                'Yes': 4,
                'No': 0,
                "Dont Know": 0
            },
            'max_marks': 4,
            'examples': {},
            'notes': '''
                If the [document] doesn't have any information asked in the question, then
                kindly answer it as "Dont Know" only. Answer it only as "Yes" or "No" only and only if the 
                [document] has an answer with respect to the question. Don't try to infer anything.
            '''
        },
        'Even after taking pain relief medication is frequently in so much pain that walking for more than 2 minutes is unbearable': {
            'options': {
                'Yes': 4,
                'No': 0,
                "Dont Know": 0
            },
            'max_marks': 4,
            'examples': {},
            'notes': '''
                If the [document] doesn't have any information asked in the question, then
                kindly answer it as "Dont Know" only. Answer it only as "Yes" or "No" only and only if the 
                [document] has an answer with respect to the question. Don't try to infer anything.
            '''
        },
        'Does the applicant gets breathless when walking up a slight hill?': {
            'options': {
                'Yes': 2,
                'No': 0,
                "Dont Know": 0
            },
            'max_marks': 2,
            'examples': {},
            'notes': '''
                If the [document] doesn't have any information asked in the question, then
                kindly answer it as "Dont Know" only. Answer it only as "Yes" or "No" only and only if the 
                [document] has an answer with respect to the question. Don't try to infer anything.
            '''
        },
        'Does the applicant gets breathless when trying to keep up with others on level ground?': {
            'options': {
                'Yes': 3,
                'No': 0,
                "Dont Know": 0
            },
            'max_marks': 3,
            'examples': {},
            'notes': '''
                If the [document] doesn't have any information asked in the question, then
                kindly answer it as "Dont Know" only. Answer it only as "Yes" or "No" only and only if the 
                [document] has an answer with respect to the question. Don't try to infer anything.
            '''
        },
        'Does the applicant gets breathless when walking on level ground at his pace?': {
            'options': {
                'Yes': 4,
                'No': 0,
                "Dont Know": 0
            },
            'max_marks': 4,
            'examples': {},
            'notes': '''
                If the [document] doesn't have any information asked in the question, then
                kindly answer it as "Dont Know" only. Answer it only as "Yes" or "No" only and only if the 
                [document] has an answer with respect to the question. Don't try to infer anything.
            '''
        },
        'Does the applicant gets breathless when getting dressed or trying to leave his home?': {
            'options': {
                'Yes': 5,
                'No': 0,
                "Dont Know": 0
            },
            'max_marks': 5,
            'examples': {},
            'notes': '''
                If the [document] doesn't have any information asked in the question, then
                kindly answer it as "Dont Know" only. Answer it only as "Yes" or "No" only and only if the 
                [document] has an answer with respect to the question. Don't try to infer anything.
            '''
        },
    }
}
