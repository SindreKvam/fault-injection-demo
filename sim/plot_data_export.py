"""This module contains code to plot simulated data."""

import argparse

import pandas as pd
import matplotlib.pyplot as plt


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Plot simulated data.")
    parser.add_argument("filename", type=str, help="Filename of the csv file.")
    parser.add_argument(
        "--sep", type=str, default="\t", help="Separator of the csv file."
    )
    parser.add_argument("--save", action="store_true", help="Save the plot.")
    args = parser.parse_args()

    df = pd.read_csv(args.filename, sep=args.sep)

    df["time"] = df["time"] * 1e6  # Convert time to microseconds

    df.plot(
        x="time",
        y=["V(5V,arduino_gnd)", "V(ctrl)"],
        label=["Arduino 5V rail", "Control signal"],
        title="Simulated voltage glitch",
        xlabel=r"Time ($\mu$s)",
        ylabel="Voltage (V)",
    )

    plt.tight_layout()
    plt.grid()
    plt.show()

    if args.save:
        plt.savefig("plot.png")
