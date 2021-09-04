import dateutil.parser as dp
from flask import Flask, request
import json
import requests

app = Flask(__name__)

CAIYUN_WEATHER_REALTIME_URL = 'https://api.caiyunapp.com/v2.5/{}/{},{}/realtime.json'
CAIYUN_WEATHER_HOURLY_URL = 'https://api.caiyunapp.com/v2.5/{}/{},{}/hourly.json?unit=metric:v1'
TOKEN = ''

SUCCESS = 0
ERR_INTERNAL_ERROR = -1
ERR_INVALID_PARAM = -2

CLEAR = 0
PARTLY_CLOUDY = 1
MOSTLY_CLOUDY = 2
CLOUDY = 3
RAINY = 4
SNOWY = 5


def create_app():
    with open('config.json') as f:
        data = json.load(f)
        TOKEN = data['token']

    @app.route('/')
    def weather():
        lat = request.args.get('lat', -1, type=float)
        lon = request.args.get('lon', -1, type=float)
        if lat < -90 or lat > 90 or lon < -180 or lon > 180:
            return {
                'status': ERR_INVALID_PARAM
            }
        else:
            try:
                content = requests.get(
                    CAIYUN_WEATHER_REALTIME_URL.format(TOKEN, lon, lat)).json()

                rain = content['result']['realtime']['skycon'].find(
                    'RAIN') != -1
                snow = content['result']['realtime']['skycon'].find(
                    'SNOW') != -1
                cloudrate = content['result']['realtime']['cloudrate']

                if snow > rain:
                    return {
                        'status': SUCCESS,
                        'result': SNOWY
                    }
                elif rain >= snow and rain > 0:
                    return {
                        'status': SUCCESS,
                        'result': RAINY
                    }
                elif cloudrate > 0.8:
                    return {
                        'status': SUCCESS,
                        'result': CLOUDY
                    }
                elif cloudrate > 0.2:
                    return {
                        'status': SUCCESS,
                        'result': PARTLY_CLOUDY
                    }
                else:
                    return {
                        'status': SUCCESS,
                        'result': CLEAR
                    }

            except:
                return {
                    'status': ERR_INTERNAL_ERROR
                }

    @app.route('/rain')
    def rain():
        lat = request.args.get('lat', -1, type=float)
        lon = request.args.get('lon', -1, type=float)
        if lat < -90 or lat > 90 or lon < -180 or lon > 180:
            return {
                'status': ERR_INVALID_PARAM
            }
        else:
            try:
                content = requests.get(
                    CAIYUN_WEATHER_HOURLY_URL.format(TOKEN, lon, lat)).json()

                precips = []
                count = 0
                for precip in content['result']['hourly']['precipitation']:
                    time = dp.parse(precip['datetime']).timestamp()
                    value = float(precip['value'])
                    precips.append({'time': time, 'value': value})

                    count += 1
                    if count >= 24:
                        break

                return {
                    'status': SUCCESS,
                    'result': precips
                }

            except:
                return {
                    'status': ERR_INTERNAL_ERROR
                }


create_app()
