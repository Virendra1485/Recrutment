FROM python:3.7
WORKDIR /usr/src/app
COPY requirements.txt /usr/src/app/
RUN pip install -q -U --prefer-binary --no-cache-dir -r requirements.txt
COPY . /usr/src/app
CMD ["python3", "app.py"]