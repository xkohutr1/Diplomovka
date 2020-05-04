FROM python:3

WORKDIR /root
COPY requirements.txt ./
RUN pip install -r requirements.txt

EXPOSE 5000

COPY . ./
ENTRYPOINT ["python", "./Python/app.py"]

# docker build C:/Users/RomanK/Desktop/DIPLOMOVKA/Docker -t romankohut/apk-for-decentralized-mpc
# docker push romankohut/apk-for-decentralized-mpc
# docker run -it --rm -p 5000:5000 romankohut/apk-for-decentralized-mpc






