# -*- mode: ruby -*-
# vi: set ft=ruby :

# Vagrantfile API/syntax version. Don't touch unless you know what you're doing!
VAGRANTFILE_API_VERSION = "2"

$goodies = <<EOF
sudo apt-get install -y vim tmux git
wget https://raw.githubusercontent.com/irifed/dotfiles-pub/master/.vimrc
wget https://raw.githubusercontent.com/irifed/dotfiles-pub/master/.tmux.conf
EOF

$prep = <<EOF
pushd /opt
sudo git clone --recursive https://github.com/irifed/vagrant-cluster.git
sudo mkdir /var/clusters
EOF

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|

    config.vm.define "dockerhost" 

    config.vm.box = "ubuntu/trusty64"

    config.vm.network "forwarded_port", guest: 8080, host: 8080

    config.vm.synced_folder "/Users/irina/Projects/github/irifed/softlayer-clustermanager", "/opt/softlayer-clustermanager"

    config.vm.provider "virtualbox" do |vb|
        vb.name = "dockerhost"
        vb.customize ["modifyvm", :id, "--cpus", "2", "--memory", "2048"]
    end

    config.vm.provision "shell", path: "https://get.docker.com/ubuntu/"
    config.vm.provision "shell", inline: $goodies
    config.vm.provision "shell", inline: $prep
end
