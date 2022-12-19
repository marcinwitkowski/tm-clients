#!/usr/bin/env python
# -*- coding: utf-8 -*-
from urllib import request, error
import json
"""
    Adress Provider provides addresses for Techmo services based on json stored in the web.
"""
__author__ = "Marcin Witkowski"
__date__ = "19.12.2022"


class AddressProvider:

    def __init__(self):
        with open('addresses.json', 'r') as jr:
            self.addresses = json.load(jr)

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
