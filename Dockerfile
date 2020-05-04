FROM python:3

WORKDIR /root
COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY . ./
ENTRYPOINT ["python", "./Python/app.py"]

EXPOSE 5000

# docker build C:/Users/RomanK/Desktop/DIPLOMOVKA/Docker -t romankohut/apk-for-decentralized-mpc
# docker push romankohut/apk-for-decentralized-mpc






