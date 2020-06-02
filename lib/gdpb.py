import logging
import json

import uhal

from .sca_module import ScaModule

logging.basicConfig(level=logging.INFO, format='%(asctime)s  %(name)s  %(levelname)s  %(message)s')
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

__author__ = "Sheng Dong"
__email__ = "s.dong@mails.ccnu.edu.cn"


class Gdpb(object):
    def __init__(self, afck_num, link):
        super(Gdpb, self).__init__()
        assert isinstance(afck_num, int)
        assert isinstance(link, int)
        assert 0 <= link < 6, "Argument link out of range, should be from 0 to 5"
        self.__afck_num = afck_num
        self.__link = link

        with open('config.json', 'r') as f:
            config = json.load(fp=f)

        connection_file_dir = config["connection_file_dir"]
        experiment_name = config["experiment_name"]
        connection_id = config["connection_id"]
        # self.connection_file_path = "/opt/dpbcontrols/etc/ipbus_lab%d_gdpb_gbtx.xml" % self.__afck_num
        self.connection_file_path = connection_file_dir + "ipbus_%s%d_gdpb_gbtx.xml" % (
            experiment_name, self.__afck_num)
        self.device_id = connection_id + "%03d" % self.__afck_num

        self.__connection_mgr = uhal.ConnectionManager("file://" + self.connection_file_path)
        self.__hw = self.__connection_mgr.getDevice(self.device_id)

        self.scaModule = ScaModule(self.__hw, self.__link)
