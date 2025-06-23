
import logging
#import paho.mqtt.client as mqtt
#paho library to handle mqtt 
import paho.mqtt.publish as publish 
import string

# Setup logging
logging.basicConfig(level=logging.INFO)





#channel_ID = " "  # Replace with your channel ID

mqtt_host = "mqtt3.thingspeak.com" # thingsSpeak URL for mqtt service, SEE https://uk.mathworks.com/help/thingspeak/mqtt-basics.html

mqtt_client_ID = "YOUR_CLIENT_ID"

mqtt_username  = "YOUR_MQTT_USERNAME"

mqtt_password  = "YOUR_MQTT_PASSWORD"

t_transport = "websockets"

t_port = 80

# function to thingsSpeak URL

def publish_to_thingspeak(temperature, humidity, rssi, snr, crc_error_count, header_error_count):

    payload = ""

    if temperature is not None:

        payload += "field1=" + str(temperature)

    if humidity is not None:

        if payload != "":

            payload += "&"

        payload += "field2=" + str(humidity)

    if rssi is not None:

        if payload != "":

            payload += "&"

        payload += "field3=" + str(rssi)

    if snr is not None:

        if payload != "":

            payload += "&"

        payload += "field4=" + str(snr)

    if crc_error_count is not None:

        if payload != "":

            payload += "&"

        payload += "field5=" + str(crc_error_count)
        
    if crc_error_count is not None:

        if payload != "":

            payload += "&"

        payload += "field6=" + str(header_error_count)



    try:

        publish.single("channels/" + channel_ID + "/publish", payload, hostname=mqtt_host, transport=t_transport, port=t_port, client_id=mqtt_client_ID, auth={'username':mqtt_username,'password':mqtt_password})

    except Exception as e:

        logging.error("Failed to publish to ThingSpeak: %s", e)


# functions to handle the incoming LoRa packets marschalling, etc 
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)

'''
def parse_lora_packet(packet):
    try:
        message = packet.decode('utf-8')
        temperature = extract_value(message, 'Temperature:', 'C')
        humidity = extract_value(message, 'Humidity:', '%')
        return temperature, humidity
    except UnicodeDecodeError as e:
        logging.error(f'Error decoding bytes: {e}')
    except ValueError as e:
        logging.error(f'Error converting to float: {e}')
    return None, None

def extract_value(message, start_tag, end_tag):
    try:
        start = message.find(start_tag) + len(start_tag)
        end = message.find(end_tag, start)
        return float(message[start:end].strip())
    except Exception as e:
        logging.error(f"error extracting from '{message}. '{start_tag}', End tag: '{end_tag}'. Error:{e}" )
        return None
'''

def parse_lora_packet(packet):
    try:
        message = packet.decode('utf-8')
        values = message.split(',')
        #Temperature and humidity will be split by ,
        if len(values) >=3:
            nodeId = values [0].strip()
            temperature = float(values[1].strip())
            humidity = float(values[2].strip())
            return nodeId, temperature, humidity
        else:
            logging.error(f"Packet format incorrect")
            return None, None, None
            
    except UnicodeDecodeError as e:
        logging.error(f'Error decoding packet: {packet}. error : {e}')
        return None, None,None
    except ValueError as e:
        logging.error(f'Error converting to float: {message}. error : {e}')
        return None, None, None

import os, sys
currentdir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.dirname(os.path.dirname(currentdir)))
from LoRaRF import SX126x
import time


# SPI Init: Begin LoRa radio and set NSS, reset, busy, IRQ, txen, and rxen pin with connected Raspberry Pi gpio pins ( with HAT) https://www.waveshare.com/sx1262-lorawan-hat.htm
# https://www.waveshare.com/sx1262-lorawan-hat.htm

busId = 0; csId = 0 
resetPin = 18; busyPin = 20; irqPin = 16; txenPin = 6; rxenPin = -1 
LoRa = SX126x()
logging.info("Begin LoRa radio")
if not LoRa.begin(busId, csId, resetPin, busyPin, irqPin, txenPin, rxenPin) :
    raise Exception("Something wrong, can't begin LoRa radio")

LoRa.setDio2RfSwitch()
# Set frequency to 868 Mhz
logging.info("Set frequency to 868 Mhz")
LoRa.setFrequency(868000000)

# Set RX gain to power saving gain
logging.info("Set RX gain to power saving gain")
LoRa.setRxGain(LoRa.RX_GAIN_POWER_SAVING)

# Configure modulation parameter including spreading factor (SF), bandwidth (BW), and coding rate (CR)
logging.info("Set modulation parameters:\n\tSpreading factor = 11\n\tBandwidth = 125 kHz\n\tCoding rate = 4/5")
sf = 7
bw = 125000
cr = 6 
LoRa.setLoRaModulation(sf, bw, cr)

# Configure packet parameter including header type, preamble length, payload length, and CRC type
logging.info("Set packet parameters:\n\tExplicit header type\n\tPreamble length = 12\n\tPayload Length = 15\n\tCRC on")
headerType = LoRa.HEADER_EXPLICIT
preambleLength = 12
payloadLength = 15
crcType = True
LoRa.setLoRaPacket(headerType, preambleLength, payloadLength, crcType)

# Set syncronize word for public network (0x3444)
logging.info("Set syncronize word to 0x3444")
LoRa.setSyncWord(0x3444)

logging.info("\n-- LoRa Receiver Continuous --\n")

# Request for receiving new LoRa packet in RX continuous mode
LoRa.request(LoRa.RX_CONTINUOUS)

# Receive message continuously
# Initialize counters for lost packets
crc_error_count = 0
header_error_count = 0

# Receive message continuously
while True:

    # Check for incoming LoRa packet
    if LoRa.available():

        # Put received packet to message and counter variable
        #message = ""
        packet = bytearray();
        while LoRa.available() > 1:
            #message += chr(LoRa.read())
           packet.append(LoRa.read())
        counter = LoRa.read()

        # Extract temperature and humidity from the message
        nodeId, temperature, humidity = parse_lora_packet(packet)
     
     # since this is not a REAL LoRa gateway I handle the data based on the ID sent from the LoRa node (no secure, have to be implemented otherwise), but for now good enough   
      # Interrupts for the radio and encrypted ID and keys would be nice to have
        if nodeId is not None:
            if nodeId == 'Your_NODE_1_ID':
                channel_ID = "Things_Speak_Channel_ID"
            elif nodeId == 'Your_Node_2_ID':
                channel_ID = "Things_Speak_Channel_ID"
            else:
                logging.warning("Unknown node name:{}".format(nodeId))

        # Immediately publish temperature and humidity if above valid by calling the mqtt/thingSpeak Functions
        if temperature is not None and humidity is not None:
            publish_to_thingspeak(temperature, humidity, None, None, None, None)

        # Print received message and counter in serial for monitoring
        logging.info(f"{packet}  {counter}")

        # Capture RSSI and SNR from RADIO for stats
        rssi = LoRa.packetRssi()
        snr = LoRa.snr()
        logging.info("Packet status: RSSI = {0:0.2f} dBm | SNR = {1:0.2f} dB".format(rssi, snr))

        # Publish RSSI and SNR
        publish_to_thingspeak(None, None, rssi, snr, None, None)

        # Check for packet errors
        status = LoRa.status()
        if status == LoRa.STATUS_CRC_ERR:
            crc_error_count += 1
            logging.info("CRC error")
        if status == LoRa.STATUS_HEADER_ERR:
            header_error_count += 1
            logging.info("Packet header error")

        # Publish error counts
        publish_to_thingspeak(None, None, None, None, crc_error_count, header_error_count)


try :
    pass
except :
    LoRa.end()

