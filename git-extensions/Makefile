
build:
	@echo nothing to do

.PHONY : install
install:
	@cp git-devbliss /usr/bin/
	@cp show-pulls /usr/bin/show-pulls
	@cp github.py /usr/bin/github-devbliss
	@chmod a+x /usr/bin/show-pulls
	@chmod a+x /usr/bin/github-devbliss
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
	@rm -f /usr/bin/github-devbliss

define changelog_cmd
	changelog="CHANGES.md"
	if [ -z "$$EDITOR" ]; then
		EDITOR=vi
	fi
	$$EDITOR $$changelog
endef
export changelog_cmd
.PHONY : changelog
changelog:
	@bash -c "$$changelog_cmd"

.PHONY : version
version:
	@bash -c "$$changelog_cmd"
