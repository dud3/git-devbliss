# -*- mode: ruby -*-
# vi: set ft=ruby :
Vagrant::Config.run do |config|
  config.vm.box = "precise64"
  config.vm.box_url = 'http://files.vagrantup.com/precise64.box'
  config.vm.host_name = "gitdevbliss"
  config.vm.define :gitdevbliss do |gitdevbliss_config|

    # share the local copy of gitdevbliss with the guest
    gitdevbliss_config.vm.share_folder "gitdevbliss", "/home/vagrant/git-devbliss", "."

    # enable symlinks in the mounted file system at /home/vagrant/git-devbliss
    gitdevbliss_config.vm.customize ["setextradata", :id, "VBoxInternal2/SharedFoldersEnableSymlinksCreate/git-devbliss", "1"]
    gitdevbliss_config.vm.customize ["modifyvm", :id, "--memory", 512]

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
