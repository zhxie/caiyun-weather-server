FROM python:3

WORKDIR /usr/src/caiyun-weather-server

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "flask", "run", "--host=0.0.0.0" ]
