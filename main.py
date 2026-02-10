import network
import urequests
import ujson
import time
from machine import Pin

# ==== CONFIGURACIÓN ====
WIFI_SSID = "TU_SSID_AQUI"
WIFI_PASSWORD = "TU_PASSWORD_AQUI"

API_KEY = "TU_API_KEY_DE_OPENWEATHERMAP"
CITY = "Barcelona"
COUNTRY_CODE = "ES"  # Código de país, por ejemplo ES, FR, etc.
UNITS = "metric"     # "metric" para ºC, "standard" o "imperial"

# LED en un pin digital (ajusta según tu conexión)
LED_PIN = 2  # En muchas placas el LED integrado está en el pin 2
led = Pin(LED_PIN, Pin.OUT)

# Intervalo entre consultas (en segundos)
UPDATE_INTERVAL = 60  # por ejemplo, 60 segundos


def conectar_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("Conectando a WiFi...")
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)
        while not wlan.isconnected():
            time.sleep(0.5)
            print(".", end="")
    print("\nConectado. Config:", wlan.ifconfig())
    return wlan


def obtener_tiempo():
    # Construimos la URL de la API
    url = (
        "http://api.openweathermap.org/data/2.5/weather"
        "?q={},{}&appid={}&units={}"
    ).format(CITY, COUNTRY_CODE, API_KEY, UNITS)

    print("Haciendo petición a:", url)
    try:
        respuesta = urequests.get(url)
        if respuesta.status_code == 200:
            datos = respuesta.json()
            respuesta.close()
            return datos
        else:
            print("Error en la respuesta HTTP:", respuesta.status_code)
            respuesta.close()
            return None
    except Exception as e:
        print("Error en la petición:", e)
        return None


def esta_lloviendo(datos_json):
    """
    Devuelve True si en weather[0].main aparece algo relacionado con lluvia.
    Por ejemplo: 'Rain', 'Drizzle', 'Thunderstorm'.
    """
    try:
        weather_main = datos_json["weather"][0]["main"]
        print("weather[0].main =", weather_main)

        # Puedes ajustar esta lógica según lo que quieras considerar "lluvia"
        condiciones_lluvia = ["Rain", "Drizzle", "Thunderstorm"]
        if weather_main in condiciones_lluvia:
            return True
        else:
            return False
    except Exception as e:
        print("Error al interpretar JSON:", e)
        return False


def actualizar_led(llueve):
    if llueve:
        print("Está lloviendo → LED ENCENDIDO")
        led.value(1)
    else:
        print("No llueve → LED APAGADO")
        led.value(0)


def main():
    conectar_wifi()

    while True:
        datos = obtener_tiempo()
        if datos:
            llueve = esta_lloviendo(datos)
            actualizar_led(llueve)
        else:
            print("No se pudieron obtener datos meteorológicos.")

        print("Esperando {} segundos para la próxima consulta...\n".format(UPDATE_INTERVAL))
        time.sleep(UPDATE_INTERVAL)


# Punto de entrada
if __name__ == "__main__":
    main()
