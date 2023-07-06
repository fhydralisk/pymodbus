"""ModbusMessage layer.

is extending ModbusTransport to handle receiving and sending of messsagees.

ModbusMessage provides a unified interface to send/receive Modbus requests/responses.
"""
from enum import Enum

from pymodbus.logging import Log
from pymodbus.transport.transport import CommParams, ModbusProtocol


class CommHeaderType(Enum):
    """Type of Modbus header"""

    SOCKET = 1
    TLS = 2
    RTU = 3
    ASCII = 4
    BINARY = 5


class ModbusMessage(ModbusProtocol):
    """Message layer extending transport layer.

    When receiving:
    - Secures full valid Modbus message is received (across multiple callbacks from transport)
    - Validates and removes Modbus header (CRC for serial, MBAP for others)
    - Decodes frame according to frame type
    - Callback with pure request/response

    When sending:
    - Encod request/response according to frame type
    - Generate Modbus message by adding header (CRC for serial, MBAP for others)
    - Call transport to do the actual sending of data

    The class is designed to take care of differences between the different modbus headers, and
    provide a neutral interface for the upper layers.
    """

    def __init__(
        self,
        headerType: CommHeaderType,
        params: CommParams,
        is_server: bool,
    ) -> None:
        """Initialize a message instance.

        :param headerType: Modbus header type
        :param params: parameter dataclass
        :param is_server: true if object act as a server (listen/connect)
        """
        params.new_connection_class = lambda: ModbusMessage(
            headerType,
            self.comm_params,
            False,
        )
        super().__init__(params, is_server)
        self.header: ModbusHeader = {
            CommHeaderType.SOCKET: HeaderSocket(self),
            CommHeaderType.TLS: HeaderTLS(self),
            CommHeaderType.RTU: HeaderRTU(self),
            CommHeaderType.ASCII: HeaderASCII(self),
            CommHeaderType.BINARY: HeaderBinary(self),
        }[headerType]

    # --------- #
    # callbacks #
    # --------- #
    def callback_data(self, data: bytes, addr: tuple = None) -> int:
        """Handle received data."""
        Log.debug("callback_data called: {} addr={}", data, ":hex", addr)
        return 0

    # ----------------------------------- #
    # Helper methods for external classes #
    # ----------------------------------- #
    def message_send(self, data: bytes, addr: tuple = None) -> None:
        """Send request.

        :param data: non-empty bytes object with data to send.
        :param addr: optional addr, only used for UDP server.
        """
        Log.debug("send: {}", data, ":hex")
        self.transport_send(data, addr=addr)

    # ---------------- #
    # Internal methods #
    # ---------------- #


class ModbusHeader:  # pylint: disable=too-few-public-methods
    """Generic header"""


class HeaderSocket(ModbusHeader):  # pylint: disable=too-few-public-methods
    """MDAP Header for socket transport"""

    def __init__(self, message):
        """Initialize"""
        self.message = message


class HeaderTLS(ModbusHeader):  # pylint: disable=too-few-public-methods
    """TLS Header for socket transport"""

    def __init__(self, message):
        """Initialize"""
        self.message = message


class HeaderRTU(ModbusHeader):  # pylint: disable=too-few-public-methods
    """RTU Header for serial/socket transport"""

    def __init__(self, message):
        """Initialize"""
        self.message = message


class HeaderASCII(ModbusHeader):  # pylint: disable=too-few-public-methods
    """ASCII Header for serial/socket transport"""

    def __init__(self, message):
        """Initialize"""
        self.message = message


class HeaderBinary(ModbusHeader):  # pylint: disable=too-few-public-methods
    """Binary Header for serial/socket transport"""

    def __init__(self, message):
        """Initialize"""
        self.message = message
