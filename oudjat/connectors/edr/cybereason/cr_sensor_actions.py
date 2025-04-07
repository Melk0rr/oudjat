from enum import Enum


class CybereasonSensorAction(Enum):
    """An enumeration of Cybereason available sensor actions"""

    ARCHIVE = "archive"
    UNARCHIVE = "unarchive"
    REMOVEFROMGROUP = "removeFromGroup"
    ADDTOGROUP = "addToGroup"
    SCHEDULERSCAN = "schedulerScan"
    UPGRADE = "upgrade"
    FETCHLOGS = "fetchLogs"
    SETRANSOMWAREMODE = "setRansomwareMode"
    SETPREVENTIONMODE = "setPreventionMode"
    SETANTIMALWARESTATUS = "set-antimalware-status"
    SETPSPROTECTIONSTATUS = "set-PowershellProtection-status"
    STARTCOLLECTION = "startCollection"
    STOPCOLLECTION = "stopCollection"
    DELETE = "delete"
    PURGESENSORS = "purgeSensors"
    REVERTPURGEDSENSORS = "revertPurgedSensors"
    RESTART = "restart"
    DOWNLOADLOGSBATCHID = "download-logs/:batchID"

