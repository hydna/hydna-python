#!/usr/bin/env python
# encoding: utf-8

from distutils.core import setup

package_data = {
    'hydna': ['cacerts/cacert.pem'],
}

setup(name='hydna', version='0.1.5', description='Python client for Hydna.',
      author='Gustaf Sjöberg', author_email='gs@hydna.com',
      url='http://www.hydna.com/', packages=['hydna'],
      package_data=package_data)
