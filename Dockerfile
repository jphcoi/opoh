FROM python:3-slim
ADD parse_SYNC.py /
ADD requirements.txt /
RUN pip install -r requirements.txt
RUN pip install python-docx
RUN python -m spacy download en_core_web_sm
CMD [ "python", "./parse_SYNC.py" ]
