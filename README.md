
# Weather epaper display

This repo contains an experiment to drive epaper display, connected to an esp32s2 chip.
we use the micropython firmware on the chip, with additional microython libraries for mqtt, and epaper spi control



![](20231108_083007.jpg)



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
	ampy --port /dev/ttyACM0 put *


## Design and implementation

ePaper display 400x300 in BW colors, in this design the esp32s2 implements a display server that offers the following primitives :

- clear() : clear the screen
- picture( p, x, y ) : display a picture at a specific location on the screen
- text (box, textstring) : display a text in a box
- update(): apply the in-buffer to the screen. (this primitive is quite slow, due to epaper technology)

These primitives are send thought **mqtt**, as **commands**, and evaluated within the **python interpreter**. see [device_code/display.py](device_code/display.py)



On the agent side ([epaper_info.py](epaper_info.py)), the screens are not directly implemented using code (too long). 

An SVG template is taken and dynamic values are replaced within the svg document (using templating) and then rasterized using **cairosvg**. 

The template is drawn in [Inkskape](https://inkscape.org/fr/), some text box are named for text replacement with [weather api content](https://openweathermap.org/). 

![](inkscape_template.png)





The whole display is then splitted into small image tiles and sent over the mqtt topic as below :

```python
p = p64("///8////wP///f///8D///z////A///8////wP///f///8D///z////A///8////wP///f///8D///z////A///8////wP///f///8D///z////A///8////wP///f///8D///z////A///8////wP///f///8D///z////A///8////wP///f///8D///z////A///8////wP///f///8D///z////A///8////wP///f///8D///z////A///8////wP///f///8D///z////A///8////wP///f///8BSlKT////AAAAA////wP///////8D////////A////////wP///////8D////////A////////wP///////8D////////A////////wP///////8D////////A////////wP///////8D////////A////////wP///////8A=", 50, 50)
d.picture(p, 350, 250)
```

After having sent all the tiles, a final d.update() is sent over the wire to materialize the reconstructed image on the screen.



