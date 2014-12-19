from flask_wtf import Form
from wtforms import StringField, SelectField, IntegerField, BooleanField
from wtforms.validators import DataRequired, Optional, InputRequired


class SLConfigForm(Form):
    # sl_username = StringField('sl_username', validators=[DataRequired()])
    # sl_api_key = StringField('sl_api_key', validators=[DataRequired()])
    cluster_name = StringField('cluster_name', validators=[DataRequired()])
    sl_ssh_key = StringField('sl_ssh_key', validators=[Optional()])

    sl_domain = StringField('sl_domain', validators=[DataRequired()])

    num_workers = IntegerField('num_workers', validators=[InputRequired()],
                               default=1)

    # ams01,dal01,dal05,dal06,dal09,hkg02,hou02,lon02,mel01,par01,sea01,sjc01,sng01,tor01,wdc01
    datacenters = [
        ('ams01', 'ams01'),
        ('dal01', 'dal01'),
        ('dal05', 'dal05'),
        ('dal06', 'dal06'),
        ('dal09', 'dal09'),
        ('hkg02', 'hkg02'),
        ('hou02', 'hou02'),
        ('lon02', 'lon02'),
        ('mel01', 'mel01'),
        ('par01', 'par01'),
        ('sea01', 'sea01'),
        ('sng01', 'sng01'),
        ('sjc01', 'sjc01'),
        ('tor01', 'tor01'),
        ('wdc01', 'wdc01')
        ]
    sl_datacenter = SelectField('sl_datacenter', choices=datacenters,
                                validators=[DataRequired()], default='dal06')

    cpus = [('1', '1'), ('2', '2'), ('4', '4'), ('8', '8'), ('12', '12'),
            ('16', '16')]
    sl_cpus = SelectField('sl_cpus', choices=cpus, validators=[DataRequired()],
                          default='1')

    memory = [('1024', '1024'), ('2048', '2048'), ('4096', '4096'),
              ('8192', '8192'),
              ('16384', '16384'), ('32768', '32768'), ('65536', '65536')]
    sl_memory = SelectField('sl_memory', choices=memory,
                            validators=[DataRequired()], default='1024')

    disk_capacity = [('25', '25'), ('100', '100')]
    sl_disk_capacity = SelectField('sl_disk_capacity', choices=disk_capacity,
                                   validators=[DataRequired()], default='25')

    network_speed = [('10', '10'), ('100', '100'), ('1000', '1000')]
    sl_network_speed = SelectField('sl_network_speed', choices=network_speed,
                                   validators=[DataRequired()], default='100')

    install_spark = BooleanField('install_spark', default=True)
    install_mapred = BooleanField('install_mapred', default=False)
    install_mesos = BooleanField('install_mesos', default=False)
    install_hive = BooleanField('install_hive', default=False)
    install_cassandra = BooleanField('install_cassandra', default=False)
    install_tachyon = BooleanField('install_tachyon', default=False)
    install_mpi = BooleanField('install_mpi', default=False)

