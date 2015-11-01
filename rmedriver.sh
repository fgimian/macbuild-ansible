#!/usr/bin/env make -f

# Update the following URL to the current RME driver as require
DRIVER = http://www.rme-audio.de/download/driver_usb_mac_2102.zip

install:
	@echo "Cleaning up any old downloaded RME drivers"
	rm -f ${TMPDIR}$(shell basename $(DRIVER))
	rm -f ${TMPDIR}$(shell basename $(DRIVER)).*
	@echo

	@echo "Downloading the RME driver from $(DRIVER)"
	wget -q -O ${TMPDIR}$(shell basename $(DRIVER)) $(DRIVER)
	@echo

	@echo "Extracting the Fireface installer"
	unzip -q -j ${TMPDIR}$(shell basename $(DRIVER)) "*Fireface USB.pkg" -d ${TMPDIR}
	rm ${TMPDIR}$(shell basename $(DRIVER))
	@echo

	@echo "Extracting the Fireface package"
	xar -xf "${TMPDIR}Fireface USB.pkg" rmeusbinstall.pkg/Payload -C ${TMPDIR}
	rm "${TMPDIR}Fireface USB.pkg"
	@echo

	@echo "Extracting installer payload"
	tar xf ${TMPDIR}rmeusbinstall.pkg/Payload -C ${TMPDIR}
	rm ${TMPDIR}rmeusbinstall.pkg/Payload
	rmdir ${TMPDIR}rmeusbinstall.pkg
	@echo

	@echo "Installing the driver into the extensions directory"
	sudo rm -rf /System/Library/Extensions/RMEFirefaceUSB.kext
	sudo tar xf ${TMPDIR}rme_usb_install.tar --strip-components=1 -C /System/Library/Extensions "rme_usb_install/RMEFirefaceUSB.kext"
	sudo touch /System/Library/Extensions
	rm ${TMPDIR}rme_usb_install.tar
	@echo

	@echo "All done, please reboot OS X so that the driver may be loaded! :)"
