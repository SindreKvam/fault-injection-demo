"""This module contains a small API for the HP6612C power supply"""

import logging

from prologix_gpib_lan import PrologixGpibLan


class Hp6612c:
    """Class for HP6612C power supply"""

    def __init__(self, ip_address: str, gpib_address: int = 5, port: int = 1234) -> None:

        self.interface = PrologixGpibLan(
            ip_address, gpib_address, port, auto=0, eoi=1, eos=2, mode=1, timeout_s=1
        )

    def set_voltage(self, voltage: float) -> None:
        """Set the output voltage of the power supply"""
        return self.interface.write(f"VOLT {voltage}")

    def get_voltage(self) -> float:
        """Get the output voltage of the power supply"""
        return float(self.interface.query("VOLT?"))

    def set_current_limit(self, current: float) -> None:
        """Set the current limit of the power supply"""
        return self.interface.write(f"CURR {current}")

    def enable_output(self) -> None:
        """Enable the output of the power supply"""
        return self.interface.write("OUTP ON")

    def disable_output(self) -> None:
        """Disable the output of the power supply"""
        return self.interface.write("OUTP OFF")

    def measure_voltage(self) -> float:
        """Measure the output voltage of the power supply"""
        return float(self.interface.query("MEAS:VOLT?"))

    def measure_current(self) -> float:
        """Measure the output current of the power supply"""
        return float(self.interface.query("MEAS:CURR?"))


# Debugging
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    power_supply = Hp6612c("172.16.1.53")

    power_supply.set_voltage(3.3)
    power_supply.enable_output()

    print(power_supply.get_voltage())

    power_supply.disable_output()
