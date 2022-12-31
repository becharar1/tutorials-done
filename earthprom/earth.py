 #The weather forecast for the next hour at Red Hat headquarters
import requests
HOURLY_RED_HAT = "http://api.weatherapi.com/v1/current.json?key= 6c2c1c19299446ef9c1110014222812&q=London&aqi=no"
def get_temperature():
    result = requests.get(HOURLY_RED_HAT)
    #print(result.json()["current"]["temp_c"])
    return result.json()["current"]["temp_c"]

#We use the Prometheus Python library to create a registry with one gauge: the temperature at Red Hat HQ.
from prometheus_client import CollectorRegistry, Gauge
def prometheus_temperature(num):
    registry = CollectorRegistry()
    g = Gauge("red_hat_temp", "Temperature at Red Hat HQ", registry=registry)
    g.set(num)
    return registry

from wsgiref.simple_server import make_server
from pyramid.config import Configurator
from pyramid.response import Response
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
def metrics_web(request):
    registry = prometheus_temperature(get_temperature())
    return Response(generate_latest(registry),
                    content_type=CONTENT_TYPE_LATEST)
config = Configurator()
config.add_route('metrics', '/metrics')
config.add_view(metrics_web, route_name='metrics')
app = config.make_wsgi_app()
server=make_server('0.0.0.0',8080,app)
server.serve_forever()
