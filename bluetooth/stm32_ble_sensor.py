import bluetooth
from stm32_bleAdvertising import adv_payload # Pour gérer l'advertising GAP
from struct import pack # Pour agréger les octets envoyés par les trames BLE
from micropython import const
import pyb # Pour gérer les LED

# Constantes définies pour le protocole Blue-ST
_IRQ_CENTRAL_CONNECT    = const(1)
_IRQ_CENTRAL_DISCONNECT = const(2) 
_IRQ_GATTS_WRITE        = const(3)

# Indique que l'on va communiquer avec une appli conforme au protocole Blue-ST :
_ST_APP_UUID = bluetooth.UUID('00000000-0001-11E1-AC36-0002A5D5C51B')

# Initialisation des LED
led_red = pyb.LED(3)
led_green = pyb.LED(2)

# 2 - Construction de la trame (contenu du message) d'avertising GAP
_PROTOCOL_VERSION = const(0x01) # Version du protocole
_DEVICE_ID = const(0x80) # Carte NUCLEO générique
_DEVICE_MAC = [0x12, 0x34, 0x56, 0x78, 0x9A, 0xBC] # Adresse matérielle MAC fictive

class BLESensor:
  # # UUID d'une caractéristique de température
  # _DEFAULT_TEMPERATURE_UUID = (bluetooth.UUID('00040000-0001-11e1-ac36-0002a5d5c51b'), bluetooth.FLAG_NOTIFY)
  # _DEFAULT_FEATURE_MASK = const(2**18)

  # Initialisation, démarrage de GAP et publication radio des trames d'advertising
  def __init__(self, ble, services, mask):
    self._services = services

    # Trame d'avertising : concaténation des informations avec la fonction Micropython "pack" 
    # La chaîne '>BBI6B' désigne le format des arguments, voir la documention de pack ici : https://docs.python.org/3/library/struct.html
    self._MANUFACTURER = pack('>BBI6B', _PROTOCOL_VERSION, _DEVICE_ID, mask, *_DEVICE_MAC)

    self._ble = ble
    self._ble.active(True)
    self._ble.irq(self._irq)

    self._connections = None
    self._payload = None
    self._handler = None

  def init_service(self, registerCallback, name='WB55-MPY'):
    self._ST_APP_SERVICE = (_ST_APP_UUID, self._services)
    registerCallback(self)
    self._connections = set()
    self._payload = adv_payload(name=name, manufacturer=self._MANUFACTURER)
    self._advertise()
    self._handler = None

  # Gestion des évènements BLE...
  def _irq(self, event, data):
    # Si un central a envoyé une demande de connexion
    if event == _IRQ_CENTRAL_CONNECT:
      conn_handle, _, _, = data
      # Se connecte au central (et arrête automatiquement l'advertising)
      self._connections.add(conn_handle)
      led_red.off()
      led_green.on()

    # Si le central a envoyé une demande de déconnexion
    elif event == _IRQ_CENTRAL_DISCONNECT:
      conn_handle, _, _, = data
      self._connections.remove(conn_handle)
      # Relance l'advertising pour permettre de nouvelles connexions
      self._advertise()
      led_red.on()
      led_green.off()

		# Si une écriture est détectée dans la caractéristique SWITCH (interrupteur) de la LED
    elif event == _IRQ_GATTS_WRITE:
      conn_handle, value_handle, = data
      if self._switch_handle:
        if conn_handle in self._connections and value_handle == self._switch_handle:
				  # Lecture de la valeur de la caractéristique
          data_received = self._ble.gatts_read(self._switch_handle)
          self._ble.gatts_write(self._switch_handle, pack('<HB', 1000, data_received[0]))
          self._ble.gatts_notify(conn_handle, self._switch_handle)
          # Selon la valeur écrite, on allume ou on éteint la LED rouge
          if data_received[0] == 1:
            pass # callback .on()
          else:
            pass # callback .off()

  # On écrit, dans la caractéristique "temperature", le timestamp (horodatage) et la valeur de la température
  def set_data(self, package, data_handle, notify=1):
    self._ble.gatts_write(data_handle, package)
    if notify:
      for conn_handle in self._connections:
        # Signale au Central (le smartphone) que la caractéristique vient d'être écrite et peut être lue
        self._ble.gatts_notify(conn_handle, data_handle)

  # Démarre l'advertising avec une période de 5 secondes, précise qu'un central pourra se connecter au périphérique
  def _advertise(self, interval_us=500000):
    self._ble.gap_advertise(interval_us, adv_data=self._payload, connectable=True)
    led_red.on()
    led_green.off()
