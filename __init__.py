# -*- coding: utf-8 -*-
import sys


try:
    sys.path.append("C:\Program Files\eclipse\plugins\org.python.pydev.core_6.4.3.201807050139\pysrc")
except:
    None


def classFactory(iface):
    from .Base import Base
    return Base(iface)
