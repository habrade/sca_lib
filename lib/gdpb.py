import logging

import uhal

from sca_module import ScaModule

logging.basicConfig(level=logging.INFO, format='%(asctime)s  %(name)s  %(levelname)s  %(message)s')
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class Gdpb(ScaModule):
    def __init__(self, afck_num, link):
        assert isinstance(afck_num, int)
        assert isinstance(link, int)
        assert 0 <= link < 6, "Argument link out of range, should be from 0 to 5"
        self.__afck_num = afck_num
        self.__link = link

        self.connection_file_path = "../dpbcontrols/etc/ipbus_lab%d_gdpb_gbtx.xml" % self.__afck_num
        self.device_id = "C0S00_gdpb%03d" % self.__afck_num

        self.__connection_mgr = uhal.ConnectionManager("file://" + self.connection_file_path)
        self.__hw = self.__connection_mgr.getDevice(self.device_id)

        super(Gdpb, self).__init__(self.__hw, self.__link)
