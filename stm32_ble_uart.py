# Objet du script : mise en oeuvre du service UART BLE de Nordic Semiconductors (NUS pour
# "Nordic UART Service").
# Sources : 
# 	https://github.com/micropython/micropython/blob/master/examples/bluetooth/ble_uart_peripheral.py
# Attente active, envoi de l'adresse MAC et réception continue de chaines de caractères
import bluetooth # Classes "primitives du BLE"
from stm32_bleAdvertising import adv_payload # Pour construire la trame d'advertising
from binascii import hexlify # Convertit une donnée binaire en sa représentation hexadécimale

# Constantes requises pour construire le service BLE UART
_IRQ_CENTRAL_CONNECT = const(1)
_IRQ_CENTRAL_DISCONNECT = const(2)
_IRQ_GATTS_WRITE = const(3)
_FLAG_WRITE = const(0x0008)
_FLAG_NOTIFY = const(0x0010)

# Définition du service UART avec ses deux caractéristiques RX et TX

_UART_UUID = bluetooth.UUID("6E400001-B5A3-F393-E0A9-E50E24DCCA9E")
_UART_TX = (
  bluetooth.UUID("6E400003-B5A3-F393-E0A9-E50E24DCCA9E"),
  _FLAG_NOTIFY, # Cette caractéristique notifiera le central des modifications que lui apportera le périphérique
)
_UART_RX = (
  bluetooth.UUID("6E400002-B5A3-F393-E0A9-E50E24DCCA9E"),
  _FLAG_WRITE, # Le central pourra écrire dans cette caractéristique
)
_UART_SERVICE = (
  _UART_UUID,
  (_UART_TX, _UART_RX),
)

# org.bluetooth.characteristic.gap.appearance.xml
_ADV_APPEARANCE_GENERIC_COMPUTER = const(128)

# Nombre maximum d'octets qui peuvent être échangés par la caractéristique RX
_MAX_NB_BYTES = const(100)

ascii_mac = None

class BLEUART:

  # Initialisations
  def __init__(self, ble, name="WB55-UART", rxbuf=_MAX_NB_BYTES):
    self._ble = ble
    self._ble.active(True)
    self._ble.irq(self._irq)
    # Enregistrement du service
    ((self._tx_handle, self._rx_handle),) = self._ble.gatts_register_services((_UART_SERVICE,))
    # Augmente la taille du tampon rx et active le mode "append"
    self._ble.gatts_set_buffer(self._rx_handle, rxbuf, True)
    self._connections = set()
    self._rx_buffer = bytearray()
    self._handler = None
    # Advertising du service :
    # On peut ajouter en option services=[_UART_UUID], mais cela risque de rendre la payload de la caractéristique trop longue
    self._payload = adv_payload(name=name, appearance=_ADV_APPEARANCE_GENERIC_COMPUTER)
    self._advertise()

    # Affiche l'adresse MAC de l'objet
    dummy, byte_mac = self._ble.config('mac')
    hex_mac = hexlify(byte_mac) 
    global ascii_mac
    ascii_mac = hex_mac.decode("ascii")
    print("Adresse MAC : %s" %ascii_mac)

  # Interruption pour gérer les réceptions
  def irq(self, handler):
    self._handler = handler

  # Surveille les connexions afin d'envoyer des notifications
  def _irq(self, event, data):
    # Si un central se connecte
    if event == _IRQ_CENTRAL_CONNECT:
      conn_handle, _, _ = data
      self._connections.add(conn_handle)
    # Si un central se déconnecte
    elif event == _IRQ_CENTRAL_DISCONNECT:
      conn_handle, _, _ = data
      if conn_handle in self._connections:
        self._connections.remove(conn_handle)
      # Redémarre l'advertising pour permettre de nouvelles connexions
      self._advertise()
    # Lorsqu'un client écrit dans une caractéristique exposée par le serveur
    # (gestion des évènements de recéption depuis le central)
    elif event == _IRQ_GATTS_WRITE:
      conn_handle, value_handle = data
      if conn_handle in self._connections and value_handle == self._rx_handle:
        self._rx_buffer += self._ble.gatts_read(self._rx_handle)
        if self._handler:
          self._handler()

  # Appelée pour vérifier s'il y a des messages en attente de lecture dans RX
  def any(self):
    return len(self._rx_buffer)

  # Retourne les catactères reçus dans RX
  def read(self, sz=None):
    if not sz:
      sz = len(self._rx_buffer)
    result = self._rx_buffer[0:sz]
    self._rx_buffer = self._rx_buffer[sz:]
    return result

  # Ecrit dans TX un message à l'attention du central
  def write(self, data):
    for conn_handle in self._connections:
      self._ble.gatts_notify(conn_handle, self._tx_handle, data)

  # Mets fin à la connexion au port série simulé
  def close(self):
    for conn_handle in self._connections:
      self._ble.gap_disconnect(conn_handle)
    self._connections.clear()

  # Pour démarrer l'advertising, précise qu'un central pourra se connecter au périphérique
  def _advertise(self, interval_us=500000):
    self._ble.gap_advertise(interval_us, adv_data=self._payload, connectable = True)
