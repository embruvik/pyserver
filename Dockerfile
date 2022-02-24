FROM python:latest
WORKDIR /gp/pyserver
COPY *.py .
COPY requirements.txt .
COPY pymodules pymodules
RUN pip install --upgrade --no-cache-dir -r requirements.txt
CMD ["python","pyserver.py"]