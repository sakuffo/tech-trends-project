FROM python:3.9
EXPOSE 3111
WORKDIR /
COPY . .
RUN pip install -r requirements.txt
RUN python init_db.py
CMD ["python", "app.py"]
