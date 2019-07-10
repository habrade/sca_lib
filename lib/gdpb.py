import uhal

from sca_module import ScaModule


class Gdpb(object):
    def __init__(self, scaNum=1):
        # ScaModule.__init__(self)
        self.__scaNum = scaNum

        self.connection_file_path = ["../dpbcontrols/etc/ipbus_lab66_gdpb_gbtx.xml", "../dpbcontrols/etc/ipbus_lab67_gdpb_gbtx.xml"]
        self.device_id = ["C0S00_gdpb066", "C0S00_gdpb067"]

        self.__connection_mgr = []
        self.__hw = []

        for index in range(self.__scaNum):
            print("index = %d" % index)
            # Creating the HwInterface
            self.__connection_mgr.append(uhal.ConnectionManager("file://" + self.connection_file_path[index]))
            self.__hw.append(self.__connection_mgr[index].getDevice(self.device_id[index]))

        self.sca_modules = []
        for index in range(self.__scaNum):
            self.sca_modules.append(ScaModule(self.__hw[index]))
