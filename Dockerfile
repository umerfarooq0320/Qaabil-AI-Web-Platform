FROM python:3.11

WORKDIR /code

# Requirements install karein
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Pura code copy karein
COPY . .

# Permissions set karein (Hugging Face requirements)
RUN chmod -R 777 /code

# Backend aur Frontend dono ko chalane ke liye command
# Hum 8000 par backend aur 7860 par streamlit chalayein ge (HF 7860 use karta hai)
CMD uvicorn app.main:app --host 0.0.0.0 --port 8000 & streamlit run frontend/Home.py --server.port 7860 --server.address 0.0.0.0
