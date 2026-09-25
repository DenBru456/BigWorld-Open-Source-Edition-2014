TARGETS = bigworld-bwmachined bigworld-devel bigworld-server bigworld-tools bigworld-web-integration
#TARGETS += bigworld-server-indie

# Default the RPM output directory to 'binary_rpms', but allow it to be
# over-written by the CI system.
RPM_DEST_DIR ?= binary_rpms

TARGETS += $(RPM_DEST_DIR)


all:: $(TARGETS)

$(RPM_DEST_DIR):
	@mkdir $@

bigworld-bwmachined: | $(RPM_DEST_DIR)
	./generate.py -d -o $(RPM_DEST_DIR) bwmachined

bigworld-devel: | $(RPM_DEST_DIR)
	./generate.py -d -o $(RPM_DEST_DIR) devel

bigworld-server: | $(RPM_DEST_DIR)
	python -m"compileall" ../../../res/scripts > /dev/null || /bin/true
	./generate.py -d -o $(RPM_DEST_DIR) server

bigworld-server-indie: | $(RPM_DEST_DIR)
	python -m"compileall" ../../../res/scripts > /dev/null || /bin/true
	./generate.py -d --indie -o $(RPM_DEST_DIR) server_indie

bigworld-tools: | $(RPM_DEST_DIR)
	python -m"compileall" ../../../tools/bwlockd > /dev/null || /bin/true
	python -m"compileall" ../ > /dev/null || /bin/true
	./generate.py -d -o $(RPM_DEST_DIR) tools --create-package-version

bigworld-web-integration: | $(RPM_DEST_DIR)
	./generate.py -d -o $(RPM_DEST_DIR) web-integration

bwmachined: bigworld-bwmachined
devel: bigworld-devel
server: bigworld-server
tools: bigworld-tools
web-integration: bigworld-web-integration
