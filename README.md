
# Weather epaper display

This repo contains an experiment to drive epaper display, connected to an esp32s2 chip.
we use the micropython firmware on the chip, with additional microython libraries for mqtt, and epaper spi control

## Expected Outcomes

- Evaluating the ease of multi device control implementation, and microython maturity
- Evaluating the deployment options to lean the install of devices

- Evaluating semantic and protocol over mqtt to control displays
- Evaluating the ease of creating new screens and design toolchain


## Installing esp32s2 device

- download the micropython firmware, and esptool.py it !

install the command line to a venv
	python3 -mvenv p3
	source p3/bin/activate
	pip3 install -r requierments_dev.txt


put the python files :

	cd device_code
	ampy --port /dev/ttyACM0 put .


