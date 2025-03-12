"""This module contains a minimal API for the Prologix GPIB-LAN controller"""

import socket
import logging

logger = logging.getLogger(__name__)


class PrologixGpibLan:
    """Communication using Prologix GPIB to LAN interface"""

    def __init__(
        self,
        ip_addr: str,
        gpib_address: int,
        port: int = 1234,
        *,
        timeout_s: int = 5,
        eoi: int = 0,
        eos: int = 3,
        auto: int = 1,
        mode: int = 1,
    ) -> None:
        """Initialize communication with Prologix GPIB to LAN interface.

        Args:
            ip_addr (str): Ip address to the GPIB to LAN device.
            gpib_address (int): GPIB address of the instrument to communicate with.
            port (int, optional): Port to the GPIB to LAN device. Defaults to 1234.
            timeout_s (int, optional): Timeout in seconds for read operations. Defaults to 5.
            eoi (int, optional): Enable EOI. Defaults to 0.
            eos (int, optional): Enable EOS. Defaults to 3.
            auto (int, optional): Enable auto read after write. Defaults to 1.
            mode (int, optional): GPIB mode. Device = 0, Controller = 1. Defaults to 1.
        """

        self.instrument = socket.socket(
            socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP
        )
        self.instrument.settimeout(timeout_s)
        self.instrument.connect((ip_addr, port))

        # Set GPIB address
        self.write(f"++addr {gpib_address}")

        # Set GPIB mode
        self.write(f"++mode {mode}")

        # Enable auto read after write
        self.write(f"++auto {auto}")

        # Keep EOI disabled
        self.eoi = eoi
        self.write(f"++eoi {eoi}")

        # Enable EOS character at the end of input to support instruments that require this
        self.write(f"++eos {eos}")

        # Set read timeout
        self.write(f"++read_tmo_ms {1000 * timeout_s}")

    def query(self, message: str, num_bytes_to_read: int = 1024) -> str:
        """Send a query to the instrument and return the response."""
        self.write(message)
        return self.read(num_bytes_to_read).decode("ascii").strip()

    def write(self, message: str) -> None:
        """Write a message to the instrument not expecting any answer."""
        encoded_message = f"{message}\n".encode("ascii")
        logger.debug("Encoded message sent to PrologixGPIB: %s", encoded_message)
        self.instrument.send(encoded_message)

    def read(self, num_bytes_to_read: int) -> bytes:
        """Read a message from the instrument."""

        if self.eoi:
            logger.debug("Read until EOI")
            self.write("++read eoi")
        else:
            logger.debug("Read until timeout")
            self.write("++read")

        read_data = self.instrument.recv(num_bytes_to_read)
        logger.debug("Read data: %s", read_data.decode("ascii"))

        return read_data
