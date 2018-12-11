#!/usr/bin/env python
# -*- coding: utf-8 -*-
from urllib import request, error
import json
"""
    Adress Provider provides addresses for Techmo services based on json stored in the web.
"""
__author__ = "Marcin Witkowski"
__date__ = "11.12.2018"


class AddressProvider:

    def __init__(self, json_url="http://149.156.121.122/~mwitkowski/addresses.json"):
        self.addresses = dict()
        try:
            with request.urlopen(json_url) as url:
                self.addresses = json.loads(url.read().decode())
        except error.HTTPError as err:
            raise Exception("There is a problem with connection with \n{}.\n"
                  " Check the internet connection.\n HTTP error: {}".format(json_url, err))
        except:
            import sys
            print("Unexpected error:", sys.exc_info()[0])
            raise

    def get(self, system_key):
        """
        Returns the address of the given system.
        :param system_key: system identifier, text
        :return: address string in format "x.x.x.x:port"
        """
        if system_key not in self.addresses:
            available_keys = list(self.addresses.keys())
            raise Exception("No system with key '{}'. Available keys:{}".format(system_key, available_keys))
        else:
            return self.addresses[system_key]
