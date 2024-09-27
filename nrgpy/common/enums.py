from enum import Enum


class LoggerType(Enum):
    """Enum for supported logger types"""
    LOGR_SOLAR = "LOGR-SOLAR"
    LOGR_MET = "LOGR-MET"
    SYMPRO = "SYMPRO"
    SYMPLUS = "SYMPLUS"
    SYMPLUS_3 = "SYMPLUS-3"
    SYMCLASSIC = "SYMCLASSIC"


class LoggerModel(Enum):
    """Enum for supported logger models"""
    LOGR_SOLAR = ("9431", "9432")
    LOGR_MET = ("9458", "9459", "9460")
    SYMPRO = ("8206")
    SYMPLUS = ("4280")
    SYMPLUS_3 = ("4941")
    SYMCLASSIC = ("3090", "3526")