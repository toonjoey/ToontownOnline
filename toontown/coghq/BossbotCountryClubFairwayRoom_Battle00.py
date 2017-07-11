# File: t (Python 2.4)

from toontown.coghq.SpecImports import *
GlobalEntities = {
    1000: {
        'type': 'levelMgr',
        'name': 'LevelMgr',
        'comment': '',
        'parentEntId': 0,
        'cogLevel': 0,
        'farPlaneDistance': 1500,
        'modelFilename': 'phase_12/models/bossbotHQ/BossbotFairwayRoom_A',
        'wantDoors': 1 },
    1001: {
        'type': 'editMgr',
        'name': 'EditMgr',
        'parentEntId': 0,
        'insertEntity': None,
        'removeEntity': None,
        'requestNewEntity': {
            'entType': 'door',
            'username': 'rurbino',
            'parentEntId': 110001,
            'entId': 110002 },
        'requestSave': None },
    0: {
        'type': 'zone',
        'name': 'UberZone',
        'comment': '',
        'parentEntId': 0,
        'scale': 1,
        'description': '',
        'visibility': [] },
    110200: {
        'type': 'battleBlocker',
        'name': '<unnamed>',
        'comment': '',
        'parentEntId': 0,
        'pos': Point3(70, 0, 0),
        'hpr': Point3(270, 0, 0),
        'scale': Vec3(1, 1, 1),
        'cellId': 0,
        'radius': 10 },
    110202: {
        'type': 'door',
        'name': '<unnamed>',
        'comment': '',
        'parentEntId': 110001,
        'pos': Point3(0, 0, 0),
        'hpr': Vec3(0, 0, 0),
        'scale': 1,
        'color': Vec4(1, 1, 1, 1),
        'isLock0Unlocked': 1,
        'isLock1Unlocked': 0,
        'isLock2Unlocked': 1,
        'isLock3Unlocked': 1,
        'isOpen': 0,
        'isOpenEvent': 0,
        'isVisBlocker': 0,
        'secondsOpen': 1,
        'unlock0Event': 0,
        'unlock1Event': 110200,
        'unlock2Event': 0,
        'unlock3Event': 0 },
    10002: {
        'type': 'nodepath',
        'name': 'props',
        'comment': '',
        'parentEntId': 0,
        'pos': Point3(0, 0, 0),
        'hpr': Vec3(0, 0, 0),
        'scale': 1 },
    110001: {
        'type': 'nodepath',
        'name': '<unnamed>',
        'comment': '',
        'parentEntId': 0,
        'pos': Point3(101.06999999999999, 0, 0),
        'hpr': Point3(270, 0, 0),
        'scale': Vec3(1, 1, 1) } }
Scenario0 = { }
levelSpec = {
    'globalEntities': GlobalEntities,
    'scenarios': [
        Scenario0] }
