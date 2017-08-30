from client import get_client
import ipywidgets as widgets
from datetime import datetime
import os
import pytz

class Light():
    def __init__(self, namespace = None, name = "light0", bw_entity = "light.ent", bw_agent = None):
        if namespace is None:
            namespace = os.environ.get('NAMESPACE')
        if namespace is None:
            raise Exception("Need to provide a namespace or set NAMESPACE")

        self._url = namespace + "/s.light/" + name + "/i.boolean/slot/state"
       
        # init light bulb 
        img_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "images")
        img_light_on_path = os.path.join(img_path, "light_on.png")
        img_light_off_path = os.path.join(img_path, "light_off.png")
        self._img_light_on = open(img_light_on_path, "rb").read()
        self._img_light_off = open(img_light_off_path, "rb").read()
        self._light = widgets.Image(
            value=self._img_light_off,
            format='png',
            width=75,
            height=120,
        )
      
        text_layout = widgets.Layout(width = "500px", height='100px')
        self._text = widgets.Textarea(
            value='',
            description='Event Log:',
            disabled=False,
            layout=text_layout,
        )
        
        # init a box widget
        items = (self._light, self._text)
        box_layout = widgets.Layout(
            display='flex',
            flex_flow='row',
            align_items='center',
            border='none',
            width='100%',
        )
        self._box = widgets.Box(children=items, layout=box_layout)
    
        # init WAVE client
        self._bw_client = get_client(agent=bw_agent, entity=bw_entity)
        self._bw_client.subscribe(self._url, self._callback)

    def display(self):
        display(self._box)

    def url(self):
        return self._url

    def _callback(self, msg):
        # print "received: ", msg.payload
        pacific = pytz.timezone('America/Los_Angeles')
        time_str = pacific.localize(datetime.now()).strftime("%Y-%m-%d %H:%M:%S (%Z)")
        from_name = msg.from_vk
        from_alias = self._bw_client.unresolveAlias(msg.from_vk)
        print from_alias
        if from_alias is not None and from_alias != "":
            from_name = from_alias
        if msg.payload.lower() == "true":
            self._append_text("[" + time_str + "] light is turned on by " + from_name)
            self._light.value = self._img_light_on
        elif msg.payload.lower() == "false":
            self._append_text("[" + time_str + "] light is turned off by " + from_name)
            self._light.value = self._img_light_off
        elif msg.payload.lower() == "toggle":
            if self._light.value is self._img_light_off:
                self._append_text("[" + time_str + "] light is toggled on by " + from_name)
                self._light.value = self._img_light_on
            elif self._light.value is self._img_light_on:
                self._append_text("[" + time_str + "] light is toggled off by " + from_name)
                self._light.value = self._img_light_off

    def _append_text(self, text):
        if self._text != "":
            text += "\n"
        self._text.value = text + self._text.value
    
class Switch():
    def __init__(self, namespace = None, name = "switch0", bw_entity = "switch.ent", bw_agent = None):
        if namespace is None:
            namespace = os.environ.get('NAMESPACE')
        if namespace is None:
            raise Exception("Need to provide a namespace or set NAMESPACE")

        self._url = namespace + "/s.switch/" + name + "/i.boolean/signal/state"
       
        # init switch 
        self._switch = widgets.ToggleButtons(
            options=['Turn On', 'Turn Off'],
            disabled=False,
            button_style='',
            tooltips=['Turn on the light', 'Turn off the light']
        )
        self._switch.value = "Turn Off"
        self._switch.observe(self._switch_on_click, 'value')
        
        text_layout = widgets.Layout(width = "500px", height='100px')
        self._text = widgets.Textarea(
            value='',
            description='Event Log:',
            disabled=False,
            layout=text_layout,
        )

        # init a box widget
        items = (self._switch, self._text)
        box_layout = widgets.Layout(
            display='flex',
            flex_flow='row',
            align_items='center',
            border='none',
            width='100%',
        )
        self._box = widgets.Box(children=items, layout=box_layout)
    
        # init WAVE client
        self._switch_bw_client = get_client(agent=bw_agent, entity=bw_entity)

    def display(self):
        display(self._box)

    def url(self):
        return self._url

    def _switch_on_click(self, change):
        time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S (%Z)")
        if change['new'] == "Turn On":
            self._append_text("[" + time_str + "] switch is turned on.")
            self._switch_bw_client.publish(self._url, (64,0,0,1), "true")
        elif change['new'] == "Turn Off":
            self._append_text("[" + time_str + "] switch is turned off.")
            self._switch_bw_client.publish(self._url, (64,0,0,1), "false")
    
    def _append_text(self, text):
        if self._text != "":
            text += "\n"
        self._text.value = text + self._text.value
