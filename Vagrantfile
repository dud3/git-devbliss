# -*- mode: ruby -*-
# vi: set ft=ruby :
Vagrant.configure("2") do |config|
  config.vm.box = "precise64"
  config.vm.box_url = 'http://files.vagrantup.com/precise64.box'
  config.vm.host_name = "gitdevbliss"
  config.vm.provider "virtualbox" do |vm|
    # enable symlinks in the mounted file system at /home/vagrant/git-devbliss
    vm.vm.customize ["setextradata", :id,
                     "VBoxInternal2/SharedFoldersEnableSymlinksCreate/git-devbliss", "1"]
    vm.vm.customize ["modifyvm", :id, "--memory", 512]
  end
  config.vm.define :gitdevbliss do |gitdevbliss_config|
    # share the local copy of gitdevbliss with the guest
    gitdevbliss_config.vm.synced_folder ".", "/home/vagrant/git-devbliss"
    gitdevbliss_config.vm.provision :puppet do |puppet|
      puppet.manifests_path = "puppet/manifests"
      puppet.manifest_file  = "git-devbliss.pp"
      puppet.facter = {"environment" => "development"}
      puppet.options = [
          '--verbose',
          #'--debug',
          ]
    end
  end
end

