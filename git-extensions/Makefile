
build:
	@echo nothing to do

install:
	@cp git-devbliss /usr/bin/
	@mkdir -p /etc/bash_completion.d/
	@cp bash_completion/git-devbliss /etc/bash_completion.d/
	@echo To enable bash completion, source '/etc/bash_completion.d/git-devbliss':
	@echo
	@echo "    echo \"source /etc/bash_completion.d/git-devbliss\" >> ~/.profile"
	@echo
	@echo done

.PHONY : version
version:
	$(eval VAR1 := $(shell date))
	@sleep 5
	$(eval VAR2 := $(shell date))
	@echo $(VAR1)
	@echo $(VAR2)