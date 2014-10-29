class SLConfig:
    def __init__(self, sl_username, sl_api_key,
                 sl_ssh_key, sl_private_key_path,
                 sl_domain, sl_datacenter,
                 cpus=4, memory=16384, disk_capacity=100, network_speed=1000):
        self.sl_username = sl_username
        self.sl_api_key = sl_api_key
        self.sl_ssh_key = sl_ssh_key
        self.sl_private_key_path = sl_private_key_path
        self.sl_domain = sl_domain
        self.sl_datacenter = sl_datacenter
        self.cpus = cpus
        self.memory = memory
        self.disk_capacity = disk_capacity
        self.network_speed = network_speed

    def create_sl_config_file(self, filepath):
        """Populate sl_config.yml with provided parameters

         # SoftLayer API credentials
         sl_username: "EDIT HERE"
         sl_api_key: "EDIT HERE"
         sl_ssh_key: "EDIT HERE"
         sl_private_key_path: "EDIT HERE"

         # custom domain
         sl_domain: "example.com"

         # datacenter where virtual servers should be provisioned
         # datacenter = [ams01,dal01,dal05,dal06,hkg02,lon02,sea01,sjc01,sng01,wdc01]
         sl_datacenter: "sjc01"

         # virtual server parameters for BDAS cluster
         # cpus = [1,2,4,8,12,16]
         # memory = [1024,2048,4096,6144,8192,12288,16384,32768,49152,65536]
         cpus: 4
         memory: 16384
         disk_capacity: 100
         network_speed: 1000

        :param filepath: sl_config.yml full path
        :return:
        """

        f = open(filepath, 'w')
        f.write('# SoftLayer API credentials\n')
        f.write('sl_username: "{}"\n'.format(self.sl_username))
        f.write('sl_api_key: "{}"\n'.format(self.sl_api_key))
        f.write('sl_ssh_key: "{}"\n'.format(self.sl_ssh_key))
        f.write('sl_private_key_path: "{}"\n'.format(self.sl_private_key_path))
        f.write('\n')
        f.write('# custom domain\n')
        f.write('sl_domain: "{}"\n'.format(self.sl_domain))
        f.write('\n')
        f.write('# datacenter where virtual servers should be provisioned\n')
        f.write('# datacenter = [ams01,dal01,dal05,dal06,hkg02,lon02,sea01,sjc01,sng01,wdc01]\n')
        f.write('sl_datacenter: "{}"\n'.format(self.sl_datacenter))
        f.write('\n')
        f.write('# virtual server parameters for BDAS cluster\n')
        f.write('# cpus = [1,2,4,8,12,16]\n')
        f.write('# memory = [1024,2048,4096,6144,8192,12288,16384,32768,49152,65536]\n')
        f.write('\n')
        f.write('cpus: {}\n'.format(self.cpus))
        f.write('memory: {}\n'.format(self.memory))
        f.write('disk_capacity: {}\n'.format(self.disk_capacity))
        f.write('network_speed: {}\n'.format(self.network_speed))

        f.close()

