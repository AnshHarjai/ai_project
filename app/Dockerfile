FROM python:3.9

WORKDIR /usr/src/app

COPY requirements.txt ./

RUN pip install -r requirements.txt

RUN python -m spacy download en_core_web_lg


COPY . .

ENTRYPOINT ["python", "app.py"]