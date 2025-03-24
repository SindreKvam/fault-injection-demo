"""This module contains code to run the timing attack."""

import argparse
import logging
import threading
import time
import os
import sys
from datetime import datetime
from enum import IntEnum

import numpy as np
import matplotlib.pyplot as plt

import dwfpy as dwf
from dwfpy.analog_input import AnalogInput
from dwfpy.digital_input import DigitalInput

from fpga.generated.uart_regs import UartRegs

logger = logging.getLogger(__name__)


SAMPLE_RATE = 100e6
BUFFER_SIZE = 8192


class GlitchResult(IntEnum):
    """Enumeration of the glitch types."""

    RESET = 0
    UNLOCKED = 1
    LOCKED = 2
    UNKNOWN = 3


def multiple_args_float_int(x):
    """Try to convert a string to float, if it fails try to convert it to an integer."""
    try:
        return float(x)
    except ValueError:
        return auto_int(x)


def auto_int(x):
    """Try to convert a string to an integer automatically selecting base."""
    return int(x, 0)


def logic_analyzer_start_acquisition(
    logic_analyzer: DigitalInput,
    *,
    sample_rate: float = SAMPLE_RATE,
    buffer_size: int = BUFFER_SIZE,
) -> None:
    """Wait for the logic analyzer to finish acquiring data."""

    logger.info("Starting Logic analyzer acquisition.")
    logic_analyzer.single(
        sample_rate=sample_rate,
        buffer_size=buffer_size,
        position=buffer_size // 2,
        configure=True,
        start=True,
    )


def scope_start_acquisition(
    scope: AnalogInput,
    *,
    sample_rate: float = SAMPLE_RATE,
    buffer_size: int = BUFFER_SIZE,
) -> None:
    """Wait for the oscilloscope to finish acquiring data."""

    logger.info("Starting oscilloscope acquisition.")
    scope.single(
        sample_rate=sample_rate, buffer_size=buffer_size, configure=True, start=True
    )


def safely_set_supply_voltage(supply, *, voltage: float = 4.0):
    """Safely set the voltage of the Analog Discovery 2 power supply."""

    supply.master_enable = False
    supply.positive.enabled = False

    supply.positive.voltage = voltage

    supply.positive.enabled = True
    supply.master_enable = True

    # Give time to enable and stabilize
    time.sleep(0.5)


def get_lock_state(logic_analyzer: DigitalInput) -> int:
    """Get the lock state of the device."""
    _lock_state = logic_analyzer.single(
        sample_rate=SAMPLE_RATE,
        sample_format=16,
        buffer_size=1024,
        configure=True,
        start=True,
    )
    _lock_state_value = int(np.mean(_lock_state))
    return _lock_state_value


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Run the timing attack.")
    parser.add_argument(
        "--com",
        type=str,
        help="Serial port of the FPGA.",
        default="/dev/tty.SLAB_USBtoUART",
    )
    parser.add_argument(
        "--debug",
        action=argparse.BooleanOptionalAction,
        help="Enable debug mode.",
        default=False,
    )
    parser.add_argument(
        "--sweep",
        help="Enable glitch parameter sweep.",
        nargs=5,
        type=multiple_args_float_int,
        metavar=(
            "voltage_start",
            "voltage_stop",
            "glitch_length_start",
            "glitch_length_stop",
            "num",
        ),
    )
    parser.add_argument(
        "--glitch-length",
        type=auto_int,
        help="Length of the glitch in clock cycles (2ns step size).",
        default=0x30,
    )
    parser.add_argument(
        "--voltage",
        type=float,
        help="Voltage level of the glitch.",
        default=4.0,
    )
    parser.add_argument(
        "--output",
        type=str,
        help="Output folder.",
        default=f"output_data_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}",
    )
    args = parser.parse_args()
    print(args)

    logging.basicConfig(format=logging.BASIC_FORMAT)

    logger.setLevel(level=logging.DEBUG if args.debug else logging.INFO)

    # Make output folder
    os.makedirs(args.output, exist_ok=True)

    # Create serial connection with the FPGA.
    uart_regs = UartRegs(port=args.com, baud_rate=115200, debug=args.debug)
    logger.info("Established connection with FPGA.")

    if args.sweep is not None:
        num_sweep_points = int(args.sweep[4])
        schmoo = np.empty((num_sweep_points, num_sweep_points))
    else:
        num_sweep_points = 1
        schmoo = np.empty((1, 1))

    # Establish connection with the Analog Discovery 2.
    with dwf.AnalogDiscovery2() as analog_discovery2:
        logger.info("Established connection with analog discovery 2.")

        # Sweep the glitch parameters
        if args.sweep is None:
            voltage_levels = [args.voltage]
            glitch_lengths = [args.glitch_length]
        else:
            voltage_levels = np.linspace(args.sweep[0], args.sweep[1], num_sweep_points)
            glitch_lengths = np.linspace(
                args.sweep[2], args.sweep[3], num_sweep_points, dtype=int
            )

        logger.debug(voltage_levels)
        logger.debug(glitch_lengths)

        if voltage_levels[-1] > 4.2:
            logger.warning("Voltage levels above 4.2V are not recommended.")
            ans = input("Are you sure you want to continue? y/n: ")
            if ans.lower() != "y":
                sys.exit(0)

        # Get the Analog Discovery 2 devices
        ad2_scope = analog_discovery2.analog_input
        ad2_supply = analog_discovery2.supplies
        ad2_logic_analyzer = analog_discovery2.digital_input

        # Configure the Analog Discovery 2 oscilloscope trigger.
        ad2_scope.setup_edge_trigger(mode="normal", channel=1, slope="falling", level=1.5)

        for volt_index, voltage_level in enumerate(voltage_levels):
            for glitch_index, glitch_length in enumerate(glitch_lengths):

                logger.info(
                    "Glitch voltage: %.2f. Glitch samples %d",
                    voltage_level,
                    glitch_length,
                )

                # Setup the Analog Discovery 2 power supply.
                safely_set_supply_voltage(ad2_supply, voltage=voltage_level)

                # Make sure that the device is locked
                lock_state_pre_attack = get_lock_state(ad2_logic_analyzer)

                # Prime the FPGA glitch signal
                uart_regs.write_regs({"start_glitch": 0, "glitch_delay": glitch_length})
                logger.info("FPGA Glitch registers set")

                # Wait for acquisition to finish
                t1 = threading.Thread(
                    target=scope_start_acquisition,
                    args=(ad2_scope,),
                )
                t1.start()

                while t1.is_alive():
                    # Reset the glitch signal
                    uart_regs.write_regs({"start_glitch": 0})

                    # Run the glitch attack
                    uart_regs.write_regs({"start_glitch": 1})
                    logger.info("FPGA Glitch attack started")

                    t1.join(timeout=1)

                oscilloscope_samples = np.array(
                    [ad2_scope[0].get_data(), ad2_scope[1].get_data()]
                )

                # Get the lock state
                lock_state_value = get_lock_state(ad2_logic_analyzer)

                time.sleep(0.5)

                # Get the lock state
                lock_state_value_delayed = get_lock_state(ad2_logic_analyzer)
                print(lock_state_pre_attack, lock_state_value, lock_state_value_delayed)

                # Save the oscilloscope samples to file
                np.savez(
                    os.path.join(
                        args.output,
                        f"scope_samples_{voltage_level:.2f}V_{glitch_length}.npz",
                    ),
                    arduino_5v_rail=oscilloscope_samples[0],
                    nmos_gate=oscilloscope_samples[1],
                    lock_state=lock_state_value,
                    lock_state_delayed=lock_state_value_delayed,
                )

                # Lock state is 0 if the device is unlocked.
                # If lock state goes from 0 to 1, we have achieved a reset.
                if lock_state_value == 0 and lock_state_value_delayed == 1:
                    logger.info("Attack result; reset device")
                    schmoo[volt_index, glitch_index] = GlitchResult.RESET
                elif lock_state_value == 0 and lock_state_value_delayed == 0:
                    logger.info("Attack unlocked device")
                    schmoo[volt_index, glitch_index] = GlitchResult.UNLOCKED
                elif lock_state_value == 1 and lock_state_value_delayed == 1:
                    logger.info("Attack locked device")
                    schmoo[volt_index, glitch_index] = GlitchResult.LOCKED
                else:
                    logger.info("Unknown attack result")
                    schmoo[volt_index, glitch_index] = GlitchResult.UNKNOWN

        print(f"Lock state: {lock_state_value}")

        np.savez(
            os.path.join(
                args.output,
                f"schmoo_{voltage_levels[0]:.2f}-{voltage_levels[-1]:.2f}V"
                + f"_{glitch_lengths[0]}-{glitch_lengths[-1]}.npz",
            ),
            schmoo=schmoo,
            voltage_levels=voltage_levels,
            glitch_lengths=glitch_lengths,
        )

        # Time step is given by the sample rate and the buffer size
        # the middle of the buffer is the time 0
        t = np.linspace(
            -BUFFER_SIZE / SAMPLE_RATE / 2, BUFFER_SIZE / SAMPLE_RATE / 2, BUFFER_SIZE
        )
        plt.plot(t, oscilloscope_samples[0], label="Arduino 5V rail")
        plt.plot(t, oscilloscope_samples[1], label="NMOS gate")
        plt.legend()

        print(schmoo)

    plt.show()
