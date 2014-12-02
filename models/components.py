class Components:
    def __init__(self, install_spark=True, install_mpi=False,
                 install_hive=False, install_mesos=False, install_mapred=False,
                 install_tachyon=False, install_cassandra=False):

        self.install_spark = install_spark
        self.install_mpi = install_mpi
        self.install_hive = install_hive
        self.install_mesos = install_mesos
        self.install_mapred = install_mapred
        self.install_tachyon = install_tachyon
        self.install_cassandra = install_cassandra

    def create_components_file(self, filepath):
        f = open(filepath, 'w')

        f.write('install_spark: {}\n'.format(self.install_spark))
        f.write('install_mpi: {}\n'.format(self.install_mpi))
        f.write('install_hive: {}\n'.format(self.install_hive))
        f.write('install_mesos: {}\n'.format(self.install_mesos))
        f.write('install_mapred: {}\n'.format(self.install_mapred))
        f.write('install_tachyon: {}\n'.format(self.install_tachyon))
        f.write('install_cassandra: {}\n'.format(self.install_cassandra))

        f.close()