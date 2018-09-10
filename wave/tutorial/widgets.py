import ipywidgets as ipw
import os
import time
import threading
import math

from IPython.display import display
from traitlets import Bool, validate, Float, Enum

_lights = {}

class Light(ipw.Box):
    state = Bool(False).tag(sync=True)
    def __init__(self, label='light-1'):
        self.labeltext = label
        self.label = ipw.Label('{0} state: {1}'.format(self.labeltext, self.state))
        img_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "")
        img_light_on_path = os.path.join(img_path, "light_on.png")
        img_light_off_path = os.path.join(img_path, "light_off.png")
        self._img_light_on = open(img_light_on_path, "rb").read()
        self._img_light_off = open(img_light_off_path, "rb").read()
        self._light = ipw.Image(
            value=self._img_light_off,
            format='png',
            width=75,
            height=120,
        )

        super(Light, self).__init__()

        #self.layout.display = 'flex'
        #self.layout.align_items = 'center'
        #self.layout.flex_flow = 'column'
        #self.layout.border = 'none'
        #self.width = '100%'
        self.children = [self._light]#, self.label]
        _lights[label] = self

        self.observe(self._togglestate, 'state')

    def _togglestate(self, change):
        if change['name'] == 'state' and change['new']:
            self.turnon()
        elif change['name'] == 'state':
            self.turnoff()

    def turnoff(self):
        self._light.value = self._img_light_off
        self.state = False
        self.label.value = '{0} state: {1}'.format(self.labeltext, 'off')

    def turnon(self):
        self._light.value = self._img_light_on
        self.state = True
        self.label.value = '{0} state: {1}'.format(self.labeltext, 'on')


class Switch(ipw.ToggleButton):
    def __init__(self, light='light-1'):
        self.value = False
        self.button = ipw.ToggleButton(value=self.value)
        super(Switch, self).__init__()
        ipw.link((_lights[light], 'state'), (self, 'value'))

        self.description = 'Turn Light Off' if self.value else 'Turn Light On'
        self.button_style = 'danger' if self.value else 'success'
        self.observe(self._togglevalue, 'value')

    def _togglevalue(self, change):
        self.description = 'Turn Light Off' if self.value else 'Turn Light On'
        self.button_style = 'danger' if self.value else 'success'

    def toggle(self):
        self.value = not self.value

class MotionSensor(ipw.Box):
    state = Bool(False).tag(sync=True)
    def __init__(self, name='motionsensor-1'):
        self.button = ipw.Button()
        self.button.on_click(self._triggermotion)
        self.button.description = 'Trigger Motion'
        self.button.style.button_color = '#d6d8db'
        img_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "")
        img_sensor = os.path.join(img_path, "motionsensor.png")
        self._img_sensor_open = open(img_sensor, "rb").read()
        self._sensorimg = ipw.Image(
            value=self._img_sensor_open,
            format='png',
            width=150,
            height=150,
        )
        super(MotionSensor, self).__init__()

        self.layout.display = 'flex'
        self.layout.align_items = 'center'
        self.layout.flex_flow = 'column'
        self.layout.border = 'solid 2px'
        self.width = '100%'
        self.children = [self._sensorimg, self.button]

    def trigger(self):
        self._triggermotion(None)

    def _triggermotion(self, event):
        # TODO: publish
        self.button.style.button_color = '#219b03'
        self.button.description = 'Occupancy Triggered!'
        self.state = True
        time.sleep(.8)
        self.state = False
        self.button.style.button_color = '#d6d8db'
        self.button.description = 'Trigger Motion'

class Thermostat(ipw.HBox):
    state = Enum(['Off',"Heating","Cooling"], default_value="Off").tag(sync=True)
    hsp = Float(70.0).tag(sync=True)
    csp = Float(73.0).tag(sync=True)
    temp = Float(72.0).tag(sync=True)
    oat = Float(0).tag(sync=True)
    occupied = Bool(False).tag(sync=True)
    def __init__(self):
        img_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "")
        img_tstat = os.path.join(img_path, "thermostat.png")
        self._img_tstat_open = open(img_tstat, "rb").read()
        self._tstat = ipw.Image(
            value=self._img_tstat_open,
            format='png',
            width=240,
            height=240,
        )
        form_item_layout = ipw.Layout(
            display='flex',
            flex_flow='row',
            width='100%',
            justify_content='flex-start'
        )
        self.observe(self._updateslider, 'hsp')
        self.observe(self._updateslider, 'csp')

        self.spslider = ipw.FloatRangeSlider(min=60, max=85, step=1.0, value=[self.hsp, self.csp], continuous_update=True, orientation='horizontal')
        self.spslider.observe(self._updatesetpoints, 'value')

        self.tempsensor = ipw.Label(value='{0:.2f}'.format(self.temp))
        self.observe(self._updatetemp, 'temp')

        self.oatsensor = ipw.Label(value='{0:.2f}'.format(self.oat))

        self.statedisplay = ipw.Label(value=self.state)
        self.observe(self._updatestate, 'state')
        self.statedisplay.observe(self._updatestatedisplay, 'value')

        self.occupiedisplay = ipw.Label(value='{0}'.format(self.occupied))
        self.observe(self._update_occupancy, 'occupied')
        def occupancy_square_wave():
            i = 0;
            while True:
                i = (i + 1) % 20
                time.sleep(1)
                self.occupied = i > 10
        occthread = threading.Thread(target=occupancy_square_wave)
        occthread.start()

        def thermostat_temp_wave():
            i = 0
            while True:
                i = (i + 1) % 180
                time.sleep(1)
                adjust = -.2 if self.state == 'Cooling' else .2 if self.state == 'Heating' else 0
                self.oat = 80 + 20*math.sin(math.radians(i))
                self.temp = self.temp + adjust + (self.oat - self.temp) * .01
        tempthread = threading.Thread(target=thermostat_temp_wave)
        tempthread.start()


        form_items = [
                ipw.VBox([self._tstat]),
                ipw.VBox([
                    ipw.Box([ipw.Label(value='Outside Temperature: '), self.oatsensor], layout=form_item_layout),
                    ipw.Box([ipw.Label(value='Inside Temperature: '), self.tempsensor], layout=form_item_layout),
                    ipw.Box([ipw.Label(value='Setpoints: '), self.spslider], layout=form_item_layout),
                    ipw.Box([ipw.Label(value='State: '), self.statedisplay], layout=form_item_layout),
                    ipw.Box([ipw.Label(value='Occupied? '), self.occupiedisplay], layout=form_item_layout),
                ]),
        ]

        super(Thermostat, self).__init__()

        self.layout.display = 'flex'
        self.layout.flex_flow = 'row'
        self.layout.border = 'solid 2px'
        #self.layout.align_items = 'center'
        #self.width = '50%'
        self.children = form_items

    def _controlloop(self):
        if self.temp < self.hsp:
            self.state = 'Heating'
        elif self.temp > self.csp:
            self.state = 'Cooling'
        else:
            self.state = 'Off'

    def update_setpoints(self, hsp, csp):
        self.hsp, self.csp = hsp, csp
        self._controlloop()

    def update_temperature(self, newtemp):
        self.temp = newtemp
        self._controlloop()


    def _updatesetpoints(self, change):
        self.hsp, self.csp = change['new']
        self._controlloop()

    def _updatestate(self, change):
        self.statedisplay.value = self.state

    def _updatetemp(self, change):
        self.tempsensor.value = '{0:.2f}'.format(change['new'])
        self.oatsensor.value = '{0:.2f}'.format(self.oat)
        self._controlloop()

    def _update_occupancy(self, change):
        self.occupiedisplay.value = '{0}'.format(change['new'])

    def _updatestatedisplay(self, change):
        self.state = change['new']

    def _updateslider(self, change):
        if change['name'] == 'csp':
            old = self.spslider.value[0]
            self.spslider.value = (old, change['new'])
        elif change['name'] == 'hsp':
            old = self.spslider.value[1]
            self.spslider.value = (change['new'], old)
        self._controlloop()
