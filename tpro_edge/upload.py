import django
import os
# django local settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE",'tpro_edge.settings')
django.setup()

from django.db import IntegrityError
import datetime
from mtpo_app.models import Site, Reading, epan_sites
import pandas as pd
import shutil
import glob
from multiprocessing import  Pool
import time
import pysftp
from os.path import basename
from datetime import datetime, timedelta
import numpy as np
from tqdm import tqdm
import logging

# FORMAT = "%(asctime)s - %(message)s"
# logging.basicConfig(filename='/home/wrdnhp/tpro_edge/wrd_minitpro/cgsw.log', filemode='a', format=FORMAT)
# log = logging.getLogger()
# log.setLevel(logging.INFO)


TS_FMT = "%Y-%m-%d %H:%M:%S"
PARENT_DIR = '/home/rohit/Desktop/dev/tpro_edge/'

WATCHDIRECTORY = "/home/rohit/Desktop/dev/tpro_edge/watch_directory/"
PROCESSED_FILES = '/home/rohit/Desktop/dev/tpro_edge/processed_files/'
JUNK = '/home/rohit/Desktop/dev/tpro_edge/JUNK/'

tday = datetime.now().date().strftime('%d%b%Y')
TDAY_JUNK = JUNK+str(tday)+'_bad_files/'
TDAY_PROCESSED = PROCESSED_FILES+str(tday)+'/'

PARAMETER_SENSOR_MAPPING = {1: "battery capacity", 2: "level",
                            3: 'hourly rainfall', 50: 'daily rainfall',
                            4: 'temperature', 5: 'evaporation',
                            6: 'wind speed',
                            7: 'wind direction', 8: 'atmospheric pressure',
                            9: 'relative humidity',
                            10: 'solar radiation', 11: 'gate sensor 1',
                            12: 'gate sensor 2',
                            13: 'gate sensor 3', 14: 'gate sensor 4',
                            15: 'gate sensor 5',
                            16: 'gate sensor 6', 17: 'gate sensor 7',
                            18: 'gate sensor 8',
                            19: 'gate sensor 9', 20: 'gate sensor 10',
                            21: 'gate sensor 11',
                            22: 'gate sensor 12', 23: 'gate sensor 13',
                            24: 'gate sensor 14',
                            25: 'gate sensor 15', 26: 'gate sensor 16',
                            27: 'gate sensor 17',
                            28: 'gate sensor 18', 29: 'gate sensor 19',
                            30: 'gate sensor 20',
                            31: 'gate sensor 21', 32: 'gate sensor 22',
                            33: 'gate sensor 23',
                            34: 'gate sensor 24', 35: 'gate sensor 25',
                            36: 'gate sensor 26',
                            37: 'gate sensor 27', 38: 'gate sensor 28',
                            39: 'gate sensor 29',
                            40: 'gate sensor 30', 41: 'gate sensor 31',
                            42: 'gate sensor 32',
                            43: 'gate sensor 33', 44: 'gate sensor 34',
                            45: 'gate sensor 35',
                            46: 'gate sensor 36', 47: 'gate sensor 37',
                            48: 'gate sensor 38',
                            49: 'gate sensor 39',
                            51: 'gate sensor 41',
                            52: 'gate sensor 42', 53: 'gate sensor 43',
                            54: 'gate sensor 44',
                            55: 'gate sensor 45', 56: 'gate sensor 46',
                            57: 'gate sensor 47',
                            58: 'gate sensor 48', 59: 'gate sensor 49',
                            60: 'gate sensor 50',
                            61: 'gate sensor 51', 62: 'gate sensor 52',
                            63: 'gate sensor 53',
                            64: 'gate sensor 54', 65: 'gate sensor 55',
                            66: 'gate sensor 56',
                            67: 'gate sensor 57', 68: 'gate sensor 58',
                            69: 'gate sensor 59',
                            70: 'gate sensor 60', 71: 'gate sensor 61',
                            72: 'gate sensor 62',
                            73: 'gate sensor 63', 74: 'gate sensor 64',
                            75: 'gate sensor 65',
                            76: 'gate sensor 66', 77: 'gate sensor 67',
                            78: 'gate sensor 68'}

PARAMETER_SENSOR_MAPPING_FOR_KOMOLINE = {
    1: "battery", 2: "water level",
    3: 'hourly rain', 50: 'daily rain',
    4: 'temperature', 5: 'evaporation', 6: 'wind speed',
    7: 'wind direction', 8: 'atmospheric pressure',
    9: 'relative humidity',
    10: 'solar radiation', 11: 'gate sensor 1',
    12: 'gate sensor 2',
    13: 'gate sensor 3', 14: 'gate sensor 4',
    15: 'gate sensor 5',
    16: 'gate sensor 6', 17: 'gate sensor 7',
    18: 'gate sensor 8',
    19: 'gate sensor 9', 20: 'gate sensor 10',
    21: 'gate sensor 11',
    22: 'gate sensor 12', 23: 'gate sensor 13',
    24: 'gate sensor 14',
    25: 'gate sensor 15', 26: 'gate sensor 16',
    27: 'gate sensor 17',
    28: 'gate sensor 18', 29: 'gate sensor 19',
    30: 'gate sensor 20',
    31: 'gate sensor 21', 32: 'gate sensor 22',
    33: 'gate sensor 23',
    34: 'gate sensor 24', 35: 'gate sensor 25',
    36: 'gate sensor 26',
    37: 'gate sensor 27', 38: 'gate sensor 28',
    39: 'gate sensor 29',
    40: 'gate sensor 30', 41: 'gate sensor 31',
    42: 'gate sensor 32',
    43: 'gate sensor 33', 44: 'gate sensor 34',
    45: 'gate sensor 35',
    46: 'gate sensor 36', 47: 'gate sensor 37',
    48: 'gate sensor 38',
    49: 'gate sensor 39',
    51: 'gate sensor 41',
    52: 'gate sensor 42', 53: 'gate sensor 43',
    54: 'gate sensor 44',
    55: 'gate sensor 45', 56: 'gate sensor 46',
    57: 'gate sensor 47',
    58: 'gate sensor 48', 59: 'gate sensor 49',
    60: 'gate sensor 50',
    61: 'gate sensor 51', 62: 'gate sensor 52',
    63: 'gate sensor 53',
    64: 'gate sensor 54', 65: 'gate sensor 55',
    66: 'gate sensor 56',
    67: 'gate sensor 57', 68: 'gate sensor 58',
    69: 'gate sensor 59',
    70: 'gate sensor 60', 71: 'gate sensor 61',
    72: 'gate sensor 62',
    73: 'gate sensor 63', 74: 'gate sensor 64',
    75: 'gate sensor 65',
    76: 'gate sensor 66', 77: 'gate sensor 67',
    78: 'gate sensor 68'}

NHP = {
    "73e0bfda": "CGSWNHP_0001",
    "73e0c798": "SAHGAON_015",
    "73e0c94a": "ARANG_005",
    "73e0d4ee": "HATI_028",
    "73e0da3c": "KASDOL_011",
    "73e0e174": "CGSWNHP_0002",
    "73e0efa6": "NANDGHAT_018",
    "73e0f202": "CGSWNHP_0003",
    "73e0fcd0": "CGSWNHP_0004",
    "73e1007c": "CGSWNHP_0005",
    "cgsw0010": "SARNGPAL_003",
    "73e11dd8": "CGSWNHP_0007",
    "73e12690": "CGSWNHP_0008",
    "73e1130a": "CGSWNHP_0006",
    "73e12842": "CGSWNHP_0009",
    "73e10eae": "73E10EAE",
    "cgsw0011a": "CGSW0011A",
    "cgsw0016": "CGSWNHP_0010",
    "cgsw0017": "CGSWNHP_0011",
    "cgsw0018": "CGSWNHP_0012",
    "cgsw0019": "CGSWNHP_0013",
    "cgsw0020": "CGSWNHP_0014",
    "cgsw0021": "CGSWNHP_0015",
    "cgsw0022": "CGSWNHP_0016",
    "cgsw0023": "CGSWNHP_0017",
    "cgsw0024": "CGSWNHP_0018",
    "cgsw0025": "CGSWNHP_0019",
    "cgsw0026": "CGSWNHP_0020",
    "cgsw0027": "CGSWNHP_0021",
    "cgsw0028": "CGSWNHP_0022",
    "cgsw0029": "CGSWNHP_0023",
    "cgsw0030": "CGSWNHP_0024",
    "cgsw0031": "CGSWNHP_0025",
    "cgsw0032": "CGSWNHP_0026",
    "cgsw0033": "CGSWNHP_0027",
    "cgsw0034": "CGSWNHP_0028",
    "cgsw0035": "CGSWNHP_0029",
    "cgsw0036": "CGSWNHP_0030",
    "cgsw0037": "GURUR_56",
    "cgsw0038": "CGSWNHP_0031",
    "cgsw0039": "CGSWNHP_0032",
    "cgsw0040": "CGSWNHP_0033",
    "cgsw0041": "CGSWNHP_0034",
    "cgsw0042": "CGSWNHP_0035",
    "cgsw0043": "CGSWNHP_0036",
    "cgsw0044": "CGSWNHP_0037",
    "cgsw0045": "CGSWNHP_0038",
    "cgsw0046": "CGSWNHP_0039",
    "cgsw0047": "Gandai_58",
    "cgsw0048": "PARSWANI_009",
    "cgsw0049": "CGSWNHP_0040",
    "cgsw0050": "KOTA_023",
    "cgsw0051": "CGSWNHP_0041",
    "cgsw0052": "AMDI_006",
    "cgsw0053": "DEOKAR_017",
    "cgsw0054": "GOREGHAT_019",
    "cgsw0055": "JAMGAON_004",
    "cgsw0056": "CGSWNHP_0042",
    "cgsw0057": "CGSWNHP_0043",
    "cgsw0058": "CGSWNHP_0044",
    "cgsw0059": "CGSWNHP_0045",
    "cgsw0060": "CGSWNHP_0046",
    "cgsw0062": "CGSW0062",
    "cgsw0062a": "CGSW0062A",
    "cgsw0063": "CGSW0063",
    "cgsw0063a": "CGSW0063A",
    "cgsw0064": "Gondly_56",
    "cgsw0065": "CGSWNHP_0049",
    "cgsw0150": "CGSWNHP_0134",
    "cgsw0068": "CGSWNHP_0052",
    "cgsw0069": "CGSWNHP_0053",
    "cgsw0070": "CGSW0070",
    "cgsw0070a": "CGSW0070A",
    "cgsw0071": "CGSWNHP_0055",
    "cgsw0072": "CGSWNHP_0056",
    "cgsw0073a": "CGSW0073A",
    "cgsw0073b": "CGSW0073B",
    "cgsw0074": "CGSWNHP_0058",
    "cgsw0075": "CGSWNHP_0059",
    "cgsw0076": "CGSWNHP_0060",
    "cgsw0077": "CGSWNHP_0061",
    "cgsw0078": "CGSWNHP_0062",
    "cgsw0079": "CGSWNHP_0063",
    "cgsw0080": "CGSWNHP_0064",
    "cgsw0081": "CGSWNHP_0065",
    "cgsw0082": "CGSWNHP_0066",
    "cgsw0083": "CGSWNHP_0067",
    "cgsw0084": "CGSWNHP_0068",
    "cgsw0085": "CGSWNHP_0069",
    "cgsw0086": "CGSWNHP_0070",
    "cgsw0087": "CGSWNHP_0071",
    "cgsw0088": "CGSWNHP_0072",
    "cgsw0089": "CGSWNHP_0073",
    "cgsw0090": "CGSWNHP_0074",
    "cgsw0091": "CGSWNHP_0075",
    "cgsw0092": "CGSWNHP_0076",
    "cgsw0093": "CGSWNHP_0077",
    "cgsw0094": "CGSWNHP_0078",
    "cgsw0095": "CGSWNHP_0079",
    "cgsw0096": "CGSWNHP_0080",
    "cgsw0097a": "CGSW0097A",
    "cgsw0097b": "CGSW0097B",
    "cgsw0097c": "CGSW0097C",
    "cgsw0097d": "CGSW0097D",
    "cgsw0097e": "CGSW0097E",
    "cgsw0097f": "CGSW0097F",
    "cgsw0098": "CGSWNHP_0082",
    "cgsw0099": "CGSWNHP_0083",
    "cgsw0100": "CGSWNHP_0084",
    "cgsw0101": "CGSWNHP_0085",
    "cgsw0102": "CGSWNHP_0086",
    "cgsw0103": "CGSWNHP_0087",
    "cgsw0104": "CGSWNHP_0088",
    "cgsw0105": "CGSWNHP_0089",
    "cgsw0106": "CGSWNHP_0090",
    "cgsw0107": "CGSWNHP_0091",
    "cgsw0108": "CGSWNHP_0092",
    "cgsw0109": "CGSWNHP_0093",
    "cgsw0110": "CGSWNHP_0094",
    "cgsw0111": "CGSWNHP_0095",
    "cgsw0112": "CGSWNHP_0096",
    "cgsw0113": "CGSWNHP_0097",
    "cgsw0114": "CGSWNHP_0098",
    "cgsw0115": "CGSWNHP_0099",
    "cgsw0116": "CGSWNHP_0100",
    "cgsw0117": "CGSWNHP_0101",
    "cgsw0118": "CGSWNHP_0102",
    "cgsw0119": "CGSWNHP_0103",
    "cgsw0120": "CGSWNHP_0104",
    "cgsw0121": "CGSWNHP_0105",
    "cgsw0122": "CGSWNHP_0106",
    "cgsw0123": "CGSWNHP_0107",
    "cgsw0124": "CGSWNHP_0108",
    "cgsw0125": "CGSWNHP_0109",
    "cgsw0126": "CGSWNHP_0110",
    "cgsw0127": "CGSWNHP_0111",
    "cgsw0128": "CGSWNHP_0112",
    "cgsw0129": "CGSWNHP_0113",
    "cgsw0130": "CGSWNHP_0114",
    "cgsw0131": "CGSWNHP_0115",
    "cgsw0132": "CGSWNHP_0116",
    "cgsw0133": "CGSWNHP_0117",
    "cgsw0134": "CGSWNHP_0118",
    "cgsw0135": "CGSWNHP_0119",
    "cgsw0136": "CGSWNHP_0120",
    "cgsw0137": "CGSWNHP_0121",
    "cgsw0138": "CGSWNHP_0122",
    "cgsw0139": "CGSWNHP_0123",
    "cgsw0140": "CGSWNHP_0124",
    "cgsw0141": "CGSWNHP_0125",
    "cgsw0142": "CGSWNHP_0126",
    "cgsw0143": "CGSWNHP_0127",
    "cgsw0144": "CGSWNHP_0128",
    "cgsw0145": "CGSWNHP_0129",
    "cgsw0146": "CGSWNHP_0130",
    "cgsw0147": "CGSWNHP_0131",
    "cgsw0148": "CGSWNHP_0132",
    "cgsw0149": "CGSWNHP_0133",
}

GATE_SITES = [
    'CGSW0011A',
    'CGSW0011B',
    'CGSW0070',
    'CGSW0072',
    'CGSW0073',
    'CGSW0073A',
    'CGSW0073B',
    'CGSW0095',
    'CGSW0095A',
    'CGSW0095B',
    'CGSW0097A',
    'CGSW0097B',
    'CGSW0097C',
    'CGSW0097D',
    'CGSW0097E',
    'CGSW0097F',
]

WRD_CG_EVAPORATION_SITES = ['cgsw0072', 'cgsw0075', 'cgsw0011a',
                            'cgsw0049', 'cgsw0077', 'cgsw0095']

WRD_PARAMETER_SENSOR_MAPPING = {1: "battery capacity", 2: "level",
                            3: 'hourly Rainfall', 301: 'daily Rainfall',
                            4: 'temperature', 5: 'evaporation', 6: 'wind speed',
                            7: 'wind direction', 8: 'atmospheric pressure',
                            9: 'relative humidity',201:"daily Rainfall",
                            10: 'solar radiation', 11: 'Gate Sensor 1',
                            12: 'Gate Sensor 2',
                            13: 'Gate Sensor 3', 14: 'Gate Sensor 4',
                            15: 'Gate Sensor 5',
                            16: 'Gate Sensor 6', 17: 'Gate Sensor 7',
                            18: 'Gate Sensor 8',
                            19: 'Gate Sensor 9', 20: 'Gate Sensor 10',
                            21: 'Gate Sensor 11',
                            22: 'Gate Sensor 12', 23: 'Gate Sensor 13',
                            24: 'Gate Sensor 14',
                            25: 'Gate Sensor 15', 26: 'Gate Sensor 16',
                            27: 'Gate Sensor 17',
                            28: 'Gate Sensor 18', 29: 'Gate Sensor 19',
                            30: 'Gate Sensor 20',
                            31: 'Gate Sensor 21', 32: 'Gate Sensor 22',
                            33: 'Gate Sensor 23',
                            34: 'Gate Sensor 24', 35: 'Gate Sensor 25',
                            36: 'Gate Sensor 26',
                            37: 'Gate Sensor 27', 38: 'Gate Sensor 28',
                            39: 'Gate Sensor 29',
                            40: 'Gate Sensor 30', 41: 'Gate Sensor 31',
                            42: 'Gate Sensor 32',
                            43: 'Gate Sensor 33', 44: 'Gate Sensor 34',
                            45: 'Gate Sensor 35',
                            46: 'Gate Sensor 36', 47: 'Gate Sensor 37',
                            48: 'Gate Sensor 38',
                            49: 'Gate Sensor 39', 50: 'daily Rainfall',
                            51: 'Gate Sensor 41',
                            52: 'Gate Sensor 42', 53: 'Gate Sensor 43',
                            54: 'Gate Sensor 44',
                            55: 'Gate Sensor 45', 56: 'Gate Sensor 46',
                            57: 'Gate Sensor 47',
                            58: 'Gate Sensor 48', 59: 'Gate Sensor 49',
                            60: 'Gate Sensor 50',
                            61: 'Gate Sensor 51', 62: 'Gate Sensor 52',
                            63: 'Gate Sensor 53',
                            64: 'Gate Sensor 54', 65: 'Gate Sensor 55',
                            66: 'Gate Sensor 56',
                            67: 'Gate Sensor 57', 68: 'Gate Sensor 58',
                            69: 'Gate Sensor 59',
                            70: 'Gate Sensor 60', 71: 'Gate Sensor 61',
                            72: 'Gate Sensor 62',
                            73: 'Gate Sensor 63', 74: 'Gate Sensor 64',
                            75: 'Gate Sensor 65',
                            76: 'Gate Sensor 66', 77: 'Gate Sensor 67',
                            78: 'Gate Sensor 68'}


def _check_dependencies():
    dir_list = [
        TDAY_PROCESSED,
        TDAY_JUNK,
    ]
    for dir in dir_list:
        if not os.path.exists(dir):
            os.makedirs(dir)


def get_file_information(file_name):
    size = os.path.getsize(file_name)
    size_of_file = size / 1024
    size_info = '%.2f KB' % size_of_file
    if size_of_file > 10:
        size_info = 'Warning: Allowed Size: 10kb, File was:%s' % size_info
    detail_txt = "File: %s Size:%s" % (os.path.basename(file_name),
                                       size_info)
    return detail_txt


class Reader():
    def __init__(self, filepath):
        self.filepath = filepath
        self.filename = basename(self.filepath)
        self.ftype = None

    def initiate(self):
        details = {}
        if (self.filename.strip().startswith('_')):
            self.prefix = self.filename.split('_')[-1].replace(".csv", "")
            self.ftype = "_komoline"
        else:
            self.prefix = self.filename.split('_')[0]
            self.ftype = "_temporary"
        get_params = getattr(self, self.ftype)
        preadings, pmters = get_params()
        params = [p.lower().strip() for p in pmters]
        readings = [
            {k.strip().lower(): v for k, v in row.items()}
            for row in preadings]

        details = {
            'params': list(params),
            'readings': readings,
            'filename': self.filepath,
            'stn_filename': self.filename,
            'prefix': self.prefix,
            'orig_params': list(pmters),
            'filetype': self.ftype,
            'file_info': get_file_information(
                self.filepath)
        }
        # print('details >>>> ',details)
        if(details):
            print('details >>>> ',details,'\n')
            self.prefix = details.get('prefix').lower()
            for reads in details.get('readings'):
                self.readings = reads
                self._send2wims()                
                try:
                    ti_m = os.path.getmtime(details.get('filename'))
                    m_ti = time.ctime(ti_m)
                    t_obj = time.strptime(m_ti)
                    file_T_stamp = time.strftime("%Y-%m-%d %H:%M:%S", t_obj)
                    reading_ts = reads['timestamp']
                    reads.pop('timestamp')

                    print('file_T_stamp >>> ',file_T_stamp)
                    print('reading_ts >>> ',reading_ts)
                
                    readingObj = Reading(site = Site.objects.get(prefix = details.get('prefix').lower()),
                                        reading = str(reads),
                                        timestamp = reading_ts,
                                        last_file_at = file_T_stamp)
                    readingObj.save()
                    
                    siteObj = Site.objects.get(prefix = details.get('prefix').lower())
                    siteObj.last_reading = str(reads)
                    siteObj.last_reading_at = reading_ts
                    siteObj.last_file_at = file_T_stamp
                    siteObj.parameters = details.get('params')

                    then = datetime.strptime(str(reading_ts), "%Y-%m-%d %H:%M:%S")
                    now  = datetime.now()
                    duration = now - then 
                    duration_in_s = duration.total_seconds() 
                    hours = divmod(duration_in_s, 3600)[0] 

                    if(int(hours) >= int(4) and int(hours) < int(48)):
                        siteObj.status = 'Delay' 
                    elif(int(hours) >= int(48)):
                        siteObj.status = 'Offline'
                    else:
                        siteObj.status = 'Live'
                    siteObj.save()

                    shutil.move(details.get('filename'), TDAY_PROCESSED + details.get('stn_filename'))
                except FileNotFoundError as err:
                    pass
                except IntegrityError as err:
                    shutil.move(details.get('filename'), TDAY_JUNK + details.get('stn_filename'))
                except:
                    shutil.move(details.get('filename'), TDAY_JUNK + details.get('stn_filename'))
            print('==================================================\n\n')



    def _send2wims(self):
        host = '203.160.138.78'
        user = 'chhattisgarh_sw'
        passwd = 'chhattisw@987'

        if self.readings:
            tmp_fpath, fname2send = self._format2wims()
            if tmp_fpath:
                try:
                    print("sending file to wrd chattisgarh test server %s, %s" % (fname2send, tmp_fpath))
                    # with pysftp.Connection(host=host,username=user,password=passwd) as sftp:
                    #     sftp.put(localpath=tmp_fpath,remotepath="/chhattisgarh_sw/%s" % fname2send,confirm=False)
                    #     sftp.close()
                    #     print('%s sent to %s FTP' % (fname2send, host))
                    os.remove(tmp_fpath)
                except FileNotFoundError:
                    print('%s file not found for test server' % fname2send)
                except Exception as err:
                    print('%s sending failed to %s FTP test server  due to : %s' % (fname2send, host, err))
                    return False
            else:
                print('no wims tmp_path detected.')
        else:
            print("File empty or error")


    def _format2wims(self):
        """ this fxn needs timestamp as a datetime object"""
        timestamp = datetime.strptime(str(self.readings.get('timestamp')), '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y %H:%M')
        # Dev-268
        if datetime.strptime(str(self.readings.get('timestamp')), '%Y-%m-%d %H:%M:%S').strftime('%M') == '30':
            print('30 min. file skipped for %s' % self.prefix)
            return None, None
        timestamp_for_filename = datetime.strptime(str(self.readings.get('timestamp')), '%Y-%m-%d %H:%M:%S').strftime("%y%m%d_%H%M%S_")
        # print('%s station reading: %s' % (self.prefix,self.readings))
        prefix = self.prefix.lower()
        get_id = NHP.get(prefix, '')
        wims_site_id = ''
        if get_id:
            wims_site_id = NHP.get(prefix, '').upper()
        else:
            print('Wims Station Id not found for: %s' % prefix)
            return False

        data_str = ['&' + prefix.upper(), timestamp, '4190098101']

        # komoline prefixes for WIMS
        komoline_prefix = ['73e1130a','73e0e174','73e12842','73e12690']
        if(prefix in komoline_prefix):
            if prefix.upper() in GATE_SITES:
                for k, v in PARAMETER_SENSOR_MAPPING_FOR_KOMOLINE.items():
                    data_str.append(str(self.readings.get(v, "--")))
            else:
                for k, v in PARAMETER_SENSOR_MAPPING_FOR_KOMOLINE.items():
                    if not v.startswith('Gate'):
                        data_str.append(str(self.readings.get(v, "--")))
                    else:
                        data_str.append(str(self.readings.get(v, "--")))
                        #continue
        else:
            if prefix.upper() in GATE_SITES:
                for k, v in PARAMETER_SENSOR_MAPPING.items():
                    data_str.append(str(self.readings.get(v, "--")))
            else:
                for k, v in PARAMETER_SENSOR_MAPPING.items():
                    if not v.startswith('Gate'):
                        data_str.append(str(self.readings.get(v, "--")))
                    else:
                        data_str.append(str(self.readings.get(v, "--")))
                        #continue


        fname2send = "CGSW_" + timestamp_for_filename + wims_site_id + ".csv"
        fpath = os.path.join('/tmp', fname2send)
        # print('data_str >>> ',data_str)
        with open(fpath, 'w') as fp:
            fp.write(','.join(data_str))
        return fpath, fname2send




    def _temporary(self):
        # print('formatting  WRD file: %s' % self.filepath)
        try:
            df = pd.read_csv(self.filepath)
            df['timestamp'] = df['Sample Date'] + " " + df['Sample Time']
            df['timestamp'] = pd.to_datetime(df['timestamp'],
                                             format="%d/%m/%Y %H:%M:%S")
            df.set_index(df['timestamp'], inplace=True)
            df.resample('H')
            df['Sample Value'] = pd.to_numeric(df['Sample Value'],
                                               errors='coerce')
            df.drop(columns=['Sample Date', 'Sample Time'], inplace=True)
            for k, v in WRD_PARAMETER_SENSOR_MAPPING.items():
                df.loc[df["Sensor ID"] == k, "Sensor ID"] = v
            params = df['Sensor ID'].unique().tolist()
            new_df = pd.DataFrame([])
            # print('params >>>>>>>>>>',df)
            for col in params:
                value_df = df[df['Sensor ID'] == col]
                values = value_df['Sample Value'].to_list()
                timestamp_dt = value_df['timestamp'].to_list()
                timestamp = [datetime.strftime(t, TS_FMT) for t in
                             timestamp_dt]
                new_df[col] = pd.Series(values)  # e.g CGSW0090 file, uneven readings
                # send timestamp in datetime format to wims function
                new_df['timestamp'] = pd.Series(timestamp)
            if self.prefix.lower() in WRD_CG_EVAPORATION_SITES:
                start_time = pd.to_datetime("20:00:00", format="%H:%M:%S").time()
                end_time = pd.to_datetime("5:00:00", format="%H:%M:%S").time()
                new_df['timestamp'] = pd.to_datetime(timestamp)
                condition = (new_df['timestamp'].dt.time >= start_time) & (new_df['timestamp'].dt.time <= end_time)
                new_df['evaporation'] = np.where(condition, 0, new_df['evaporation'])
                readings = new_df.to_dict(orient='records')
                for reading in readings:
                    current_value = reading.get('evaporation')
                    temp = current_value
                    epan_obj = epan_sites.objects.get(site = Site.objects.get(prefix = self.prefix.lower()))
                    prev_value = epan_obj.previous_value
                    # print('%s previous evaporation value %s ' % (self.prefix, prev_value))
                    try:
                        if prev_value:
                            current_value = float(prev_value) - float(current_value)
                            if current_value < 0:
                                current_value = 0.0
                            # print('%s evaporation current value : %s' % (self.prefix, current_value))
                            reading.update({'evaporation': current_value})
                            # print('%s evaporation value updated for %s' % (self.prefix, reading))
                        epan_obj.previous_value = temp
                        epan_obj.save()
                    except Exception as err:
                        pass
                        # print('%s evaporation not updated due to error : %s' % (self.prefix, err))
            else:
                readings = new_df.to_dict(orient='records')
            
            return readings, params
        except pd.errors.EmptyDataError:
            # print("WRD file empty %s" % self.filepath)
            return {}, []

        except Exception as err:
            # print("wrd formatting error %s" % self.filepath)
            # print(err)
            return {}, []


    def _komoline(self):
        try:
            df_ = pd.read_csv(self.filepath, header=None)
            df = df_.iloc[:, : 7]
            df.columns = ["Satellite Id",
                          "timestamp", "Serial Number",
                          "Battery", "Water level",
                          "Hourly Rain", "Daily rain"]
            df['timestamp'] = pd.to_datetime(df['timestamp'],
                                             format="%d/%m/%y %H:%M")
            df['timestamp'] = df['timestamp'].astype(str)
            cols = ['Battery', 'Water level', 'Hourly Rain', 'Daily rain']
            df[cols] = df[cols].apply(pd.to_numeric, errors='coerce')
            df.drop(df.columns[[0, 2]], axis=1, inplace=True)
            readings = df.to_dict(orient='records')
            params = df.columns.to_list()
            params.remove('timestamp')
            return readings, params
        except Exception as err:
            pass






def main():
    tic = time.time()
    _check_dependencies()
    path = WATCHDIRECTORY
    all_csv = glob.glob(path + "/*.csv")
    all_json = glob.glob(path + "/*.json")
    all_files = all_csv + all_json
    for f in tqdm(all_files[:]):
        observer = Reader(os.path.join(path, os.path.basename(f)))
        observer.initiate()
        time.sleep(0.5)

    # toc = time.time()
    # print('Done in {:.4f} seconds'.format(toc - tic))



if __name__ == "__main__":
    print('Starting the process to process files')
    main()
    print('Process completed')