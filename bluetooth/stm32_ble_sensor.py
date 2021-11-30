# Objet du script : Implémentation du protocole Blue-ST pour un périphérique
# Définition d'un service _ST_APP_SERVICE avec quatre caractéristiques :
# 1 - SWITCH : pour éteindre et allumer une LED du périphérique depuis un central
# 2 - PRESSURE : pour envoyer une mesure de pression absolue du périphérique à un central
# 3 - HUMIDITY : pour envoyer une mesure d'humidité relative du périphérique à un central
# 4 - TEMPERATURE : pour envoyer une mesure de température du périphérique à un central

import bluetooth  # Bibliothèque bas niveau pour la gestion du BLE
from stm32_bleAdvertising import adv_payload  # Pour gérer l'advertising GAP
from struct import pack  # Pour agréger les octets envoyés par les trames BLE
from micropython import const  # Pour définir des constantes entières
import pyb  # Pour gérer les LED de la NUCLEO-WB55

# Constantes pour construire le service GATT Blue-ST du périphérique

_IRQ_CENTRAL_CONNECT = const(1)
_IRQ_CENTRAL_DISCONNECT = const(2)
_IRQ_GATTS_WRITE = const(3)

# Pour les UUID et les codes, on se réfère à la documentation du SDK Blue-ST disponible ici :
# https://www.st.com/resource/en/user_manual/dm00550659-getting-started-with-the-bluest-protocol-and-sdk-stmicroelectronics.pdf.

# 1 - Définition du service personnalisé selon le SDK Blue-ST

# Indique que l'on va communiquer avec une application qui se conforme au protocole Blue-ST
_ST_APP_UUID = bluetooth.UUID("00000000-0001-11E1-AC36-0002A5D5C51B")

# UUID d'une caractéristique de température
_ENV_UUID = (
  bluetooth.UUID("001C0000-0001-11E1-AC36-0002A5D5C51B"),
  bluetooth.FLAG_NOTIFY,
)

# UUID d'une caractéristique d'interrupteur
_SWITCH_UUID = (
  bluetooth.UUID("20000000-0001-11E1-AC36-0002A5D5C51B"),
  bluetooth.FLAG_NOTIFY | bluetooth.FLAG_WRITE,
)

_ST_APP_SERVICE = (_ST_APP_UUID, (_ENV_UUID, _SWITCH_UUID))

# 2 - Construction de la trame (contenu du message) d'avertising GAP

_PROTOCOL_VERSION = const(0x01)
_DEVICE_ID = const(0x80)  # Carte NUCLEO générique
_FEATURE_MASK = const(
  0x201C0000
)  # Switch (2^29), pressure (2^20), humidity (2^19), temperature (2^18)

# Calcul des masques
# Caractéristique SWITCH : 2^29 =      100000000000000000000000000000 (en binaire) = 20000000  (en hexadécimal)
# Caractéristique PRESSURE : 2^20 =    000000000100000000000000000000 (en binaire) = 100000    (en hexadécimal)
# Caractéristique HUMIDITY : 2^19 =    000000000010000000000000000000 (en binaire) = 80000     (en hexadécimal)
# Caractéristique TEMPERATURE : 2^18 = 000000000001000000000000000000 (en binaire) = 40000     (en hexadécimal)
# On fait la somme bit à bit :
# _FEATURE_MASK :            100000000111000000000000000000 (en binaire) = 201C0000  (en hexadécimal)

_DEVICE_MAC = [0x12, 0x34, 0x56, 0x78, 0x9A, 0xBC]  # Adresse matérielle MAC fictive

# Trame d'avertising : concaténation des informations avec la fonction Micropython "pack"
# La chaîne '>BBI6B' désigne le format des arguments, voir la documentation de pack ici : https://docs.python.org/3/library/struct.html
_MANUFACTURER = pack(
  ">BBI6B", _PROTOCOL_VERSION, _DEVICE_ID, _FEATURE_MASK, *_DEVICE_MAC
)

# Initialisation des LED
led_bleue = pyb.LED(3)
led_rouge = pyb.LED(1)


class BLESensor:

  # Initialisation, démarrage de GAP et publication radio des trames d'advertising
  def __init__(self, ble, name="WB55"):
    self._ble = ble
    self._ble.active(True)
    self._ble.irq(self._irq)
    ((self._env_handle, self._switch_handle),) = self._ble.gatts_register_services(
      (_ST_APP_SERVICE,)
    )
    self._connections = set()
    self._payload = adv_payload(name=name, manufacturer=_MANUFACTURER)
    self._advertise()
    self._handler = None

  # Gestion des évènements BLE...
  def _irq(self, event, data):

    # Si un central a envoyé une demande de connexion
    if event == _IRQ_CENTRAL_CONNECT:
      (
        conn_handle,
        _,
        _,
      ) = data
      self._connections.add(conn_handle)
      print("Connected")
      led_bleue.on()

    # Si le central a envoyé une demande de déconnexion
    elif event == _IRQ_CENTRAL_DISCONNECT:
      (
        conn_handle,
        _,
        _,
      ) = data
      self._connections.remove(conn_handle)
      # Relance l'advertising pour permettre de nouvelles connexions
      self._advertise()
      print("Disconnected")

    # Si une écriture est détectée dans la caractéristique SWITCH (interrupteur) de la LED
    elif event == _IRQ_GATTS_WRITE:
      (
        conn_handle,
        value_handle,
      ) = data
      if conn_handle in self._connections and value_handle == self._switch_handle:
        # Lecture de la valeur de la caractéristique
        data_received = self._ble.gatts_read(self._switch_handle)
        self._ble.gatts_write(
          self._switch_handle, pack("<HB", 1000, data_received[0])
        )
        self._ble.gatts_notify(conn_handle, self._switch_handle)
        # Selon la valeur écrite, on allume ou on éteint la LED rouge
        if data_received[0] == 1:
          led_rouge.on()
        else:
          led_rouge.off()

  # On écrit dans la caractéristique environnementale
  # Points d'ATTENTION :
  # - Les valeurs doivent être transmises dans l'ordre des ID des caractéristiques (pression : 20 eme bit, humidité : 19 eme bit, température 18 eme bit)
  # - Attention à la chaîne de formattage de la fonction Python "pack", égale ici à '<HiHh', voir la documentation de "pack" en Python.
  def set_data_env(self, timestamp, pressure, humidity, temperature, notify):
    self._ble.gatts_write(
      self._env_handle, pack("<HiHh", timestamp, pressure, humidity, temperature)
    )
    if notify:
      for conn_handle in self._connections:
        # Signale au central que les valeurs des caractéristiques viennent d'être rafraichies et, donc, peuvent être lues
        self._ble.gatts_notify(conn_handle, self._env_handle)

  # Pour démarrer l'advertising avec une période de 5 secondes, précise qu'un central pourra se connecter au périphérique
  def _advertise(self, interval_us=500000):
    self._ble.gap_advertise(interval_us, adv_data=self._payload, connectable=True)
    led_bleue.off()
