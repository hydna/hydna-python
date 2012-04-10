# Hydna Python Client Library

This first version of our client library for Python implements support for the
Hydna Push API. Future versions will include support for the full set of
features.

More info: https://www.hydna.com/

## Installation

Install the package using pip (preferred method):

    pip install hydna

Or download the package and install manually:

    python setup.py install

## Usage

The `hydna`-package exposes two functions:

    import hydna

    # send a message
    hydna.push('public.hydna.net/1122556827', 'test')

    # emit a signal
    hydna.emit('public.hydna.net/1122556827', 'test')
