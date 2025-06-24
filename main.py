
###################################################################
#################### Import #######################################

## W-LAN ##
import network
## Umwandlung Python - JSON ##
import ujson
## Basis Netzwerkverbindung ##
import usocket
## MQTT-Client ##
from umqtt.simple import MQTTClient
## Busverarbeitung ##
import dht
from machine import Pin
## Deepsleep ##
from machine import deepsleep
## Time ##
import time
## OTA ##
from ota import OTAUpdater

###################################################################
#################### Variablen ####################################

temp = 0  # Temperatur
hum  = 0  # Feuchtigkeit

###################################################################
#################### Pinbelegung ##################################

# Stromversorgung des DHT11
power_pin_dht = Pin(25, Pin.OUT)
# Initialisiere den DHT11
sensor_dht = dht.DHT11(Pin(4))

###################################################################
#################### Verbindungsinformationen #####################

# W-LAN Verbindungsinformationen
ssid = "BZTG-IoT"
password = "WerderBremen24"

# MQTT-Broker Verbindungsinformationen
BROKER = "192.168.1.170" # Zugewiesene IP für den Laptop (Eingabeaufforderung befehl ipconfig; IP4v Adresse)
CLIENT_ID = "127.0.0.1"

client = MQTTClient(CLIENT_ID, BROKER)
wlan   = network.WLAN(network.STA_IF)

###################################################################
############ MQTT-Broker-Ereichbarkeit Prüfen #####################

try:
    usocket.getaddrinfo("127.0.0.1", 1883)
    print("Broker erreichbar")
except:
    print("Broker nicht erreichbar")

###################################################################
############ OTA Updater ##########################################
    
ota_updater = OTAUpdater(
    ssid="BZTG-IoT",
    password="WerderBremen24",
    repo_url="https://github.com/HannesRuhe/O.T.A/",
    filename="main.py")

###################################################################
############ MQTT-Client initialisieren ###########################

def MQTT():
    
    global CLIENT_ID
    global BROKER
    global client

    print("Verbinde mit MQTT-Broker...")
    client.connect()
    print("Mit MQTT-Broker verbunden")

###################################################################
#### W-LAN verbinden im Station Interface Modus (als Client) ######

def WLAN():
    
    global ssid
    global password
    global wlan
    
    wlan.active(True)
    wlan.connect(ssid, password)

    versuche = 10
    while not wlan.isconnected() and versuche > 0:
        print("Verbinde mit WLAN...")
        time.sleep(1)
        versuche = versuche - 1

    if wlan.isconnected():
        print("Verbunden, IP:", wlan.ifconfig()[0])
    else:
        print("Verbindung fehlgeschlagen")

###################################################################
#### W-LAN + MQTT Disconnecten ####################################
        
def Disconnect():
    
    global client
    global wlan
    
    # MQTT trennen
    client.disconnect()
    print("MQTT-Verbindung getrennt.")

    # WLAN trennen
    wlan.disconnect()
    wlan.active(False)
    print("WLAN-Verbindung getrennt.")
    
###################################################################
#################### Daten Messen #################################

def TempMessung():
    
    global temp
    global hum
    global power_pin_dht
    global sensor_dht
    
    # DHT Sensor aktivieren
    power_pin_dht.value(1)
    time.sleep(0.5)
    
    sensor_dht.measure()             # Messung durchführen
    temp = sensor_dht.temperature()  # Temperatur in °C
    hum  = sensor_dht.humidity()     # Luftfeuchtigkeit in %
    
    # DHT Sensor deaktivieren
    power_pin_dht.value(0)

    print("Temperatur: {} °C, Luftfeuchtigkeit: {} %".format(temp, hum))
        
###################################################################
#################### Daten in JSON umwandeln ###################### 
    
    # JSON-Daten erstellen
    daten_für_publish = {"Temperatur": f"{temp}",
                         "Feuchtigkeit": f"{hum}"}
    
    # JSON-Daten in String umwandeln
    payload_publish = ujson.dumps(daten_für_publish)
    
    # Den Payload zurückgeben
    return payload_publish

###################################################################
#################### Hauptprogramm ################################
        
while True:
    #WLAN()
    ota_updater.download_and_install_update_if_available()
    MQTT()
    topic_publish = "Energie-Sparer-Daten"
    message_publish = TempMessung()
    client.publish(topic_publish, message_publish)
    Disconnect()
    deepsleep(5000) # Angabe in Millisekunden
