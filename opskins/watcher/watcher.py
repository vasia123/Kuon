#!/usr/bin/python
# -*- coding: utf-8 -*-
import logging
import threading
from time import time, sleep

from opskins.api.api_response import LockedDict
from opskins.api.interfaces import ISales
from opskins.watcher import Settings
from opskins.watcher.currency import Currency
from opskins.watcher.notifications import Telegram
from opskins.watcher.notifications.mail import Mail
from opskins.watcher.settings import NotificationType
from opskins.watcher.tracker import Tracker


class Watcher(threading.Thread):
    """
    Watcher class to watch tracked items and notify the user on reached conditions
    """

    _mail = None
    _telegram = None

    def __init__(self, log_level=logging.ERROR):
        """Initializing function

        :param log_level:
        """
        super().__init__()

        # initialize logger
        logging.basicConfig(level=log_level)
        self.logger = logging.getLogger("opskins_watcher")

        self.sales_interface = ISales()
        self._item_tracker = Tracker()
        self.notified_ids = []

        self.validate_settings()
        self.run()

    def run(self):
        """The main function, checking the tracked items in a while True loop

        :return:
        """
        while True:
            start_time = time()

            for tracked_item in self._item_tracker.tracked_items:
                results = self.sales_interface.search(tracked_item.search_word)
                for search_item in results.response.sales:

                    if search_item.id in self.notified_ids:
                        # if we reach the part where we already notified the user
                        # we can break the loop
                        self.logger.debug("already notified user about item: {item}".format(item=search_item.id))
                        break

                    if self.is_condition_matching(item=search_item, condition=tracked_item):
                        # condition matches and user didn't get notified yet
                        self.logger.info("conditions ({conditions}) met for item: {item}".format(
                            conditions=tracked_item, item=search_item.id))
                        self.notify_user(item=search_item)

                    else:
                        # Currently only price conditions are implemented so we can break if the condition is not met
                        # since the default sorting is ascending by price
                        self.logger.info("conditions ({conditions}) not met for item: {item}".format(
                            conditions=tracked_item, item=search_item.id))
                        break

            duration = time() - start_time
            if duration < Settings.check_frequency:
                self.logger.info("sleeping '{:.2f}' seconds".format(Settings.check_frequency - duration))
                sleep(Settings.check_frequency - duration)

    def is_condition_matching(self, item: LockedDict, condition: LockedDict):
        """Check if the set condition matches on the passed item

        :param item:
        :param condition:
        :return:
        """
        # ToDo: implement
        return False

    def notify_user(self, item: LockedDict):
        """Notifying the user with the selected option

        :param item:
        :return:
        """
        if item.id in self.notified_ids:
            return False

        item_link = "https://opskins.com/?loc=shop_view_item&item={0:d}".format(item.id)

        if Settings.notification_type == NotificationType.Nothing:
            self.logger.info('Search conditions met on item:\n<a href="{item_link}">{name}({price})</a>'.format(
                item_link=item_link, name=item.market_name, price=Currency(item.amount)))

        if Settings.notification_type == NotificationType.Telegram:
            self.telegram.send_message(
                'Search conditions met on item:\n<a href="{item_link}">{name}({price})</a>'.format(
                    item_link=item_link, name=item.market_name, price=Currency(item.amount)),
                Settings.Notification.Telegram.chat_id, parse_mode="HTML")

        if Settings.notification_type == NotificationType.Mail:
            self.mail.send_message("Search conditions met on item", '<a href="{item_link}">{name}({price})</a>'.format(
                item_link=item_link, name=item.market_name, price=Currency(item.amount)))

            raise NotImplementedError("Mail notification is not implemented yet")

        self.notified_ids.append(item.id)

    def validate_settings(self):
        """Validate the settings and overwrite the invalid settings

        :return:
        """
        if Settings.check_frequency < (60 / Settings.LIMIT_60_SECONDS):
            self.logger.info("check frequency was too high, set to {0:d}s".format(60 / Settings.LIMIT_60_SECONDS))
            Settings.check_frequency = 60 / Settings.LIMIT_60_SECONDS

    @property
    def mail(self):
        """Property for Mail class to only initialize it on usage"""
        if not self._mail:
            self._mail = Mail()
        return self._mail

    @property
    def telegram(self):
        """Property for Telegram class to only initialize it on usage"""
        if not self._telegram:
            self._telegram = Telegram()
        return self._telegram
