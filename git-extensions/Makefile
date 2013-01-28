
build:
	@echo nothing to do

install:
	@cp git-devbliss /usr/bin/
	@cp show-pulls /usr/bin/show-pulls
	@chmod a+x /usr/bin/show-pulls
	@mkdir -p /etc/bash_completion.d/
	@cp bash_completion/git-devbliss /etc/bash_completion.d/
	@echo To enable bash completion, source '/etc/bash_completion.d/git-devbliss':
	@echo
	@echo "    echo \"source /etc/bash_completion.d/git-devbliss\" >> ~/.profile"
	@echo
	@echo done
