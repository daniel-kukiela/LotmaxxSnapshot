# Copyright (c) 2020 LotmaxxSnapshot
# The LotmaxxSnapshot plugin is released under the terms of the AGPLv3 or higher.

from . import LotmaxxSnapshot


def getMetaData():
    return {}


def register(app):
    return {"extension": LotmaxxSnapshot.LotmaxxSnapshot()}