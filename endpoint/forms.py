from flask_wtf import Form
from wtforms import StringField, SelectField, IntegerField, BooleanField
from wtforms.validators import DataRequired, Optional


class SLConfigForm(Form):
    # sl_username = StringField('sl_username', validators=[DataRequired()])
    # sl_api_key = StringField('sl_api_key', validators=[DataRequired()])
    cluster_name = StringField('cluster_name', validators=[DataRequired()])
    sl_ssh_key = StringField('sl_ssh_key', validators=[Optional()])

    sl_domain = StringField('sl_domain', validators=[DataRequired()])

    num_workers = IntegerField('num_workers', validators=[DataRequired()],
                               default=1)

    # TODO add all datacenters
    datacenters = [('dal06', 'dal06'), ('sjc01', 'sjc01'), ('ams01', 'ams01')]
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
    install_hadoopmr = BooleanField('install_hadoopmr', default=False)
    install_hive = BooleanField('install_hive', default=False)
    install_cassandra = BooleanField('install_cassandra', default=False)
    install_tachyon = BooleanField('install_tachyon', default=False)
    install_mpi = BooleanField('install_mpi', default=False)

