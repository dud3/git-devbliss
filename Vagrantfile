# -*- mode: ruby -*-
# vi: set ft=ruby :
Vagrant::Config.run do |config|
  config.vm.box = "precise64"
  config.vm.box_url = 'http://files.vagrantup.com/precise64.box'
  config.vm.host_name = "workflow"
  config.vm.define :workflow do |workflow_config|

    # share the local copy of workflow with the guest
    workflow_config.vm.share_folder "workflow", "/home/vagrant/workflow", "."

    # enable symlinks in the mounted file system at /home/vagrant/workflow
    workflow_config.vm.customize ["setextradata", :id, "VBoxInternal2/SharedFoldersEnableSymlinksCreate/workflow", "1"]
    workflow_config.vm.customize ["modifyvm", :id, "--memory", 512]

    workflow_config.vm.provision :puppet do |puppet|
      puppet.manifests_path = "puppet/manifests"
      puppet.manifest_file  = "workflow.pp"
      puppet.facter = {"environment" => "development"}
      puppet.options = [
          '--verbose',
          #'--debug',
          ]
    end
  end
end
