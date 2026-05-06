# uMux_IF_Chain_SW

Microwave Multiplexer Intermediate Frequency Conversion Chain Software

## Setup for Development

With your development UV python environment active navigate to the top directory and run

``` terminal
uv add --editable --active --dev .
```

the more normal method using "-e" with pip install no longer functions unless you use a setup.py. the active flag means it will install it in the currently active env.

## Installation

One can use pip to install the package.

Run below line in terminal at the folder level with setup.py

``` terminal
uv pip install .
```

## Simple Script to run

The most basic script to run is the startup_script which can do a couple simple tasks like initialize the IF_Boards, turn base_band loop back on and off and so forth.

```terminal
uMux_IF_Chain-startup_script tcp://192.168.0.50:5025 -i 
```

NOTE: If interfaced through a Raspberry PI, the port is 2021

Connect via usb cable ot the host computer, it will show up as a serial com port. Below is an example for a Windows OS. 

```terminal
uMux_IF_Chain-startup_script serial:///COM4 -i 
```

There is a simple gui that can also be ran that can be used to interface to the IF_Boards. This is useful for tuning the LO Nulling values. It accepts the same URL like argument.
