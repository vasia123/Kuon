#!/usr/bin/python
# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod


class SalesAdapterBase:
    __metaclass__ = ABCMeta

    @abstractmethod
    def search(self, market_name):
        """Search for a specific item

        :param market_name:
        :return:
        """
        pass

    @abstractmethod
    def search_no_delay(self, market_name):
        """Search for a specific item without delay
        (some APIs delay responses to prevent bot sniping, use workarounds)

        :param market_name:
        :return:
        """
        pass

    @abstractmethod
    def get_sold_history(self, market_name):
        """Get the last available sell history

        :param market_name:
        :return:
        """
        pass

    @abstractmethod
    def get_sold_history_no_delay(self, market_name):
        """Get the last available sell history without delay
        (some APIs delay responses to prevent bot sniping, use workarounds)

        :param market_name:
        :return:
        """
        pass