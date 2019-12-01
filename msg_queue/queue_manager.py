#!/usr/bin/env python
# coding: utf-8

from multiprocessing.managers import BaseManager

class QueueManager(BaseManager):
    SHARED_PORT = 33355
    MINICAP_PORT = 1313