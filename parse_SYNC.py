import os
import spacy
import docx
import io
import pandas as pd
#from tqdm import tqdm
from collections import Counter
from bs4 import BeautifulSoup
import numpy as np
import requests
from io import BytesIO

def download_word_file(url):
    response = requests.get(url)
    if response.status_code == 200:
        return BytesIO(response.content)
    else:
        raise Exception("Failed to download the remote Word document.")

def flatten_list(_2d_list):
    flat_list = []
    # Iterate through the outer list
    for element in _2d_list:
        if type(element) is list:
            # If the element is of type list, iterate through the sublist
            for item in element:
                flat_list.append(item)
        else:
            flat_list.append(element)
    return flat_list


def correct_paragraphs(paragraphs):
    speakers=[]
    for x in paragraphs:
        speakers.append(x[1]['speaker'])
    counter = Counter(speakers)
    #print (counter)
    speaker_list=[x for x in counter if counter[x]>=5]
    paragraphs_bis=[]
    mem='%%%%DDD%%%'
    for x in paragraphs:
        if x[1]['speaker'] not in speaker_list:
            x[1]['speaker']=mem[:]
        mem=x[1]['speaker']
        paragraphs_bis.append(x)
    return paragraphs_bis

def process_paragraph(par,sync=False):
    ts='unknown'
    if sync:
        ts=par[1:9]
        #print(ts)
        par=par[11:]
    par_begin=par[:50]
    if par[:3].strip()=='Q:':
        if par[:4].strip()=='Q: [':
            #print("weird Q:",par)
            pass
        return par[3:].strip(),0,ts,'interviewer'
    elif len(par.split(' ')[0])>0:
        if ':' in par_begin:
            narrator=par.split(':')[0].split(']')[-1].strip()
            return ':'.join(par.split(':')[1:]),1,ts,narrator
        else:
            return par,-1,ts,''
    else:
        return par,-1,ts,''

narrator_dict={-1:'header',0:'interviewer',1:'interviewee'}

def parse_paragraphs(filename):
    #print (filename)
    sync=False
    if 'SYNC_' in filename or '_SYNC' in filename:
        sync=True
    narrator=-1
    paragraphs=[]
    i=0
    question_index=0
    narratoring='interviewer'
    if 'http' in filename:

        #filename = urllib3.urlopen(filename)
        filename = download_word_file(filename)

        #htmlSource = sock.read()
        #filename = requests.get(filename, allow_redirects=True).content

    for par in docx.Document(filename).paragraphs:
        i+=1
        part=par.text
        #print (len(part))
        if len(part)>0:
            par,narr,ts,narrator_name=process_paragraph(part,sync)
            par=par.strip()
            if narrator_name!='':
                narratoring=narrator_name
            if narr>=0:
                if narr==0 and narrator!=0:
                    question_index+=1
                narrator=narr
            ##print( '***\n',i,narrator,':\t',par)
            if sync:
                paragraphs.append((par,{'narrator':narrator_dict[narrator],"question_index":question_index,"ts":ts,"speaker":narratoring}))
            else:
                paragraphs.append((par,{'narrator':narrator_dict[narrator],"question_index":question_index}))
    return paragraphs



#userName = os.getenv("User_Name")
try:
    filename  = os.getenv("File_Name")
    #print('filename',filename,filename[0])
except:
    filename="/Users/jpcointet/Dropbox/Mac/Desktop/OPOH/Original17/Chu_Steven_20201014_session1_SYNC.docx"

#filename="/Users/jpcointet/Dropbox/Mac/Desktop/OPOH/Original17/Chu_Steven_20201014_session1_SYNC.docx"
#filename="Chu_Steven_20201014_session1_SYNC.docx"
#filename="https://jphcoi.github.io/enquete_vie_sociale_donnees/Chu_Steven_20201014_session1_SYNC.docx"

#filename='/Users/jpcointet/Dropbox/Mac/Desktop/OPOH/Original17bis/Sutley_Nancy_20210611_session1_SYNC.docx'
#filename='/Users/jpcointet/Dropbox/Mac/Desktop/OPOH/Original17bis/Sutley_Nancy_20210804_session2_SYNC.docx'
#paragraphs=correct_paragraphs(parse_paragraphs(filename))

#create an exogeneous index of interviewees
i=0

rows_sync=[]
filename_v=filename.split('/')[-1].split('_')
#print("filename_v",filename_v)
prefix=filename_v[0]
doc_paragraph=correct_paragraphs(parse_paragraphs(filename))
interviewee=' '.join(filename.split('/')[-1].split('20')[0].split('_')[0:])
#print("interviewee",interviewee)
session_number=str(filename_v[-2].split('.doc')[0][-1])
rows_sinc=[]
for j,par in enumerate(doc_paragraph):
        j=j+1
        rows_sync.append([i,j,par[0],par[1]['narrator'],int(par[1]['question_index']),par[1]['ts'],session_number,filename.split('/')[-1].split('.docx')[0],interviewee,par[1]['speaker']])

opoh=pd.DataFrame(rows_sync,columns=['interview_id','in_session_paragraph_id', 'text', "narrator","in_session_question_index",'timestamp','session','filename_sync','interviewee','speaker'])

#print(opoh.speaker.value_counts())
#print(opoh.session.value_counts())


import re
def clean_par(par):
    return re.sub("[\(\[].*?[\)\]]", "", par).strip()
opoh['text_clean']=opoh['text'].apply(clean_par)
opoh['length']=opoh.text_clean.apply(len)



nlp = spacy.load("en_core_web_sm", disable=["tagger", "attribute_ruler", "lemmatizer"])
doc_ents=[]
docs_enriched=[]
#for paragraphs in tqdm(opoh.text_clean.values):
for doc in nlp.pipe(opoh.text_clean.values, disable=["tok2vec", "tagger", "parser", "attribute_ruler", "lemmatizer"]):
        doc_ent=[]
        soup = BeautifulSoup(doc.text, 'html.parser')
        doc_enriched=doc.text
        my_ents_positions=[]
        for ent in doc.ents:
            doc_ent.append((ent.text, ent.label_))
            my_ents_positions.append((ent.start_char,ent.end_char))


        idx_keep = [0] + np.array(my_ents_positions).ravel().tolist() + [-1]
        idx_keep = np.array(idx_keep).reshape(-1,2)

        keep_text = ''
        i=-1
        for start_char, end_char in idx_keep:
            i+=1

            if i<len(doc_ent):
                d_ent=doc_ent[i]
                keep_text += doc_enriched[start_char:end_char] + f"<{d_ent[1]}::{d_ent[0]}>{d_ent[0]}</{d_ent[1]}>"
            else:
                keep_text += doc_enriched[start_char:]


        #print (doc,doc_ent)
        doc_ents.append(doc_ent)
        docs_enriched.append(keep_text)



counter = Counter()
#print(counter)  # Counter()

# Counter with initial values
counter_people = Counter([(u,v) for (u,v) in flatten_list(doc_ents) if v=="PERSON"])
#for x in counter_people.most_common(20):
#    print(x[0][0],x[1])


counter_event = Counter([(u,v) for (u,v) in flatten_list(doc_ents) if v=="EVENT"])
counter_org = Counter([(u,v) for (u,v) in flatten_list(doc_ents) if v=="ORG"])
counter_gpe = Counter([(u,v) for (u,v) in flatten_list(doc_ents) if v=="GPE"])
counter_fac = Counter([(u,v) for (u,v) in flatten_list(doc_ents) if v=="FAC"])

N=200
top_people = counter_people.most_common(N)
top_event = counter_event.most_common(N)
top_org = counter_org.most_common(N)
top_gpe = counter_gpe.most_common(N)
top_fac = counter_fac.most_common(N)


top_event=list(map(lambda x: x[0][0], top_event))
top_people=list(map(lambda x: x[0][0], top_people))
top_org=list(map(lambda x: x[0][0], top_org))
top_gpe=list(map(lambda x: x[0][0], top_gpe))
top_fac=list(map(lambda x: x[0][0], top_fac))
#print (top_people)

events, peoples, orgs, gpes, facs= [],[],[],[],[]
for doc_ent in doc_ents:
    event, people, org, gpe, fac =  [],[],[],[],[]
    for ent in doc_ent:
        if ent[1]=='EVENT':
            event.append(ent[0])
        if ent[1]=='PERSON':
            people.append(ent[0])
        if ent[1]=='ORG':
            org.append(ent[0])
        if ent[1]=='GPE':
            gpe.append(ent[0])
        if ent[1]=='FAC':
            fac.append(ent[0])
    events.append(list(set(event)))
    peoples.append(list(set(people)))
    orgs.append(list(set(org)))
    gpes.append(list(set(gpe)))
    facs.append(list(set(fac)))


#opoh['events']=events
opoh['events']=[[y for y in x if y in top_event] for x in events]
#opoh['peoples']=peoples
opoh['people']=[[y for y in x if y in top_people] for x in peoples]
#opoh['facs']=facs
opoh['facs']=[[y for y in x if y in top_fac] for x in facs]
#opoh['gpes']=gpes
opoh['gpes']=[[y for y in x if y in top_gpe] for x in gpes]
#opoh['orgs']=orgs
opoh['orgs']=[[y for y in x if y in top_org] for x in orgs]


def add_tag(plain_text):
    soup = BeautifulSoup(plain_text, 'html.parser')
    for term, tag in general_dict.items():
    # find all occurrences of the term in the soup object
        if len(soup.find_all(text=re.compile(r'\b{}\b'.format(term))))>0:
            #print(soup.find_all(text=re.compile(r'\b{}\b'.format(term))))
            pass
        for match in soup.find_all(text=re.compile(r'\b{}\b'.format(term))):
            #pass
            #print ('***',str(match))
        #for match in soup.find_all(text=lambda text: text and term in plain_text):
        # wrap the term with the corresponding tag
            match.replace_with(str(match).replace(term, f"<{tag}::{term}>{term}</{tag}>"))
    return soup.text


opoh['enriched_text']=docs_enriched#opoh.text.apply(add_tag)


dtype_int={}
for x in [x for x in opoh.columns if '_id' in x or '_index' in x]:
    #print(x)
    dtype_int[x]="int"
opoh[list(dtype_int.keys())]=opoh[list(dtype_int.keys())].fillna(0)
opoh.astype(dtype_int)

def get_last(string):
    return string.split('/')[-1].strip()
opoh.interviewee=opoh.interviewee.apply(get_last)

#opoh=opoh[['interviewee','session',"timestamp",'in_session_question_index','in_session_paragraph_id','text','filename_sync','speaker']]

#print(opoh.head())
#print(opoh.columns)
#print(filename.split('/')[-1]+'_parsed.csv')
opoh.to_csv(filename.split('/')[-1]+'_parsed.csv',index=False)
opoh.transpose().to_json(filename.split('/')[-1]+'_parsed.json')

#print ("data created")


def jsonfy():
    print(opoh.transpose().to_json())
    

if __name__ == '__main__':
    jsonfy()
