Introduction
============

.. image:: https://readthedocs.org/projects/adafruit-circuitpython-htu21d/badge/?version=latest
    :target: https://circuitpython.readthedocs.io/projects/htu21d/en/latest/
    :alt: Documentation Status

.. image:: https://img.shields.io/discord/327254708534116352.svg
    :target: https://discord.gg/nBQh6qu
    :alt: Discord

.. image:: https://travis-ci.org/adafruit/Adafruit_CircuitPython_HTU21D.svg?branch=master
    :target: https://travis-ci.org/adafruit/Adafruit_CircuitPython_HTU21D
    :alt: Build Status

This driver enables you to use the Adafruit HTU21D-F temperature and
humidity breakout with CircuitPyton.

Dependencies
=============
This driver depends on:

* `Adafruit CircuitPython <https://github.com/adafruit/circuitpython>`_
* `Bus Device <https://github.com/adafruit/Adafruit_CircuitPython_BusDevice>`_

Please ensure all dependencies are available on the CircuitPython filesystem.
This is easily achieved by downloading
`the Adafruit library and driver bundle <https://github.com/adafruit/Adafruit_CircuitPython_Bundle>`_.

Usage Example
=============

.. code:: python

    import time
    import board
    import busio
    from adafruit_htu21d import HTU21D

    # Create library object using our Bus I2C port
    i2c = busio.I2C(board.SCL, board.SDA)
    sensor = HTU21D(i2c)


    while True:
        print("\nTemperature: %0.1f C" % sensor.temperature)
        print("Humidity: %0.1f %%" % sensor.relative_humidity)
        time.sleep(2)

Contributing
============

Contributions are welcome! Please read our `Code of Conduct
<https://github.com/adafruit/Adafruit_CircuitPython_HTU21D/blob/master/CODE_OF_CONDUCT.md>`_
before contributing to help this project stay welcoming.

Building locally
================

Zip release files
-----------------

To build this library locally you'll need to install the
`circuitpython-build-tools <https://github.com/adafruit/circuitpython-build-tools>`_ package.

.. code-block:: shell

    python3 -m venv .env
    source .env/bin/activate
    pip install circuitpython-build-tools

Once installed, make sure you are in the virtual environment:

.. code-block:: shell

    source .env/bin/activate

Then run the build:

.. code-block:: shell

    circuitpython-build-bundles --filename_prefix adafruit-circuitpython-htu21d --library_location .

Sphinx documentation
-----------------------

Sphinx is used to build the documentation based on rST files and comments in the code. First,
install dependencies (feel free to reuse the virtual environment from above):

.. code-block:: shell

    python3 -m venv .env
    source .env/bin/activate
    pip install Sphinx sphinx-rtd-theme

Now, once you have the virtual environment activated:

.. code-block:: shell

    cd docs
    sphinx-build -E -W -b html . _build/html

This will output the documentation to ``docs/_build/html``. Open the index.html in your browser to
view them. It will also (due to -W) error out on any warning like Travis will. This is a good way to
locally verify it will pass.
