
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

.PHONY : uninstall
uninstall:
	@rm -f /usr/bin/git-devbliss
	@rm -f /usr/bin/show-pulls
	@rm -f /etc/bash_completion.d/git-devbliss

define changelog_cmd
	changelog="CHANGES.md"
	if [ -z "$$EDITOR" ]; then
		EDITOR=vi
	fi
	ch_hash=$$(sha1sum $$changelog)
	$$EDITOR $$changelog
	ch_hash_new=$$(sha1sum $$changelog)
	if [ "$$ch_hash" == "$$ch_hash_new" ]; then
		echo "Operation aborted due to missing changelog entry" > /dev/stderr
		exit 1
	fi
endef
export changelog_cmd
.PHONY : changelog
changelog:
	@bash -c "$$changelog_cmd"

.PHONY : version
version:
	@bash -c "$$changelog_cmd"
