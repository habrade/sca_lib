import uhal

from sca_module import ScaModule


class Gdpb(ScaModule):
    def __init__(self, num_sca=1):
        ScaModule.__init__(self)
        self.__num_sca = num_sca

        self.connection_file_path = ["../dpbcontrols/etc/ipbus_lab66_gdpb_gbtx.xml"]
        self.device_id = ["C0S00_gdpb066"]

        self.__connection_mgr = []
        self.__hw = []

        for index in range(self.__num_sca):
            # Creating the HwInterface
            self.__connection_mgr[index] = uhal.ConnectionManager("file://" + self.connection_file_path[index])
            self.__hw[index] = self.__connection_mgr.getDevice(self.device_id[index])

        self.sca_modules = []
        for index in range(self.__num_sca):
            self.sca_modules[index] = ScaModule(self.__hw[index])
