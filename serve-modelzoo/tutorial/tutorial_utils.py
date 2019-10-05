import PIL
import numpy as np
import io
import requests
import json
import base64
from pprint import pprint

def _add_noise_to_img(img_bytes):
    """A helper method to add noise to image"""
    img = PIL.Image.open(io.BytesIO(img_bytes))
    arr = np.array(img)
    arr += np.random.randint(0,2, size=arr.shape, dtype=arr.dtype).reshape(arr.shape)
    arr -= np.random.randint(0,2, size=arr.shape, dtype=arr.dtype).reshape(arr.shape)
    arr = arr.clip(min=0, max=255)
    new_img = PIL.Image.fromarray(arr)
    byte_io = io.BytesIO()
    new_img.save(byte_io, 'PNG')
    return byte_io.getvalue()

def _get_bounding_boxes(output_string):
    """Yield Rectangle object from output string"""
    import re
    import matplotlib.patches as patches
    bbox_regex = re.compile(r" ([a-z]+): [\d]{2}%\n Left: ([\d]{1,3}), Bottom: ([\d]{1,3}), Right: ([\d]{1,3}), Top: ([\d]{1,3})")
    matched = bbox_regex.findall(output_string)
    
    colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k']
    for c, m in zip(colors, matched):
        cat, left, bottom, right, top = m
        left, bottom, right, top = int(left), int(bottom), int(right), int(top)
        yield patches.Rectangle((left,bottom), right-left, top-bottom, linewidth=1, facecolor='none', edgecolor=c,label=cat)

def plot_bbox(im_name, output_string, download=False):
    """Plot the image with bbox overlay"""
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches
    from PIL import Image
    import numpy as np
    fig,ax = plt.subplots(1, figsize=(10,8))
    if download:
        from io import BytesIO
        response = requests.get(im_name)
        ax.imshow(np.array(Image.open(BytesIO(response.content))))
    else:
        ax.imshow(np.array(Image.open(im_name)))
    for p in _get_bounding_boxes(output_string):
        ax.add_patch(p) 
    plt.title("Prediction result for image: {}".format(im_name))
    fig.legend()

def predict_and_plot(im_name, clipper_addr):
    """Make a prediction and plot image with bbox"""
    url = "http://%s/darknet-app/predict" % clipper_addr
    req_json = json.dumps({
        "input":
        base64.b64encode(open(im_name, "rb").read()).decode() # bytes to unicode
    })
    headers = {'Content-type': 'application/json'}
    r = requests.post(url, headers=headers, data=req_json)
    pprint(r.json())
    plot_bbox(im_name, r.json()['output'])

def predict_and_plot_url(im_url, clipper_addr):
    """Make a prediction and plot image (downloaded from im_url) with bbox"""
    url = "http://%s/darknet-app/predict" % clipper_addr
    req_json = json.dumps({
        "input":
        base64.b64encode(requests.get(url=im_url).content).decode() # bytes to unicode
    })
    headers = {'Content-type': 'application/json'}
    r = requests.post(url, headers=headers, data=req_json)
    pprint(r.json())
    plot_bbox(im_url, r.json()['output'], download=True)

def setup_grafana(grafana_url, metric_addr):
    # 1. Perform Auth
    response = requests.post(f'http://admin:admin@{grafana_url}/api/auth/keys', 
                            data=json.dumps({"Role": "Admin", "Name":"new_api_key"}),
                            headers={"Content-type": "application/json"})
    if not response.ok:
        print("Request to generate API Key failed:", response.json()['message'])
    key = response.json()['key']

    # 2. Add DataSource
    data_source_body = json.dumps({
        "name":"Clipper Metrics",
        "type":"prometheus",
        "url":f"http://{metric_addr}",
        "access":"proxy"
    })

    response = requests.post(f'http://{grafana_url}/api/datasources',
                             data=data_source_body,
                             headers={"Content-type": "application/json", 
                                     "Accept": "application/json",
                                     "Authorization": "Bearer %s" % (key)})
    if not response.ok:
        print("Request to add Data Source failed:", response.json()['message'])

    # 3. Add Dashboard
    with open('Clipper-Dashboard.json', 'r') as myfile:
        dashboard_source_body=myfile.read()

    response = requests.post(f'http://{grafana_url}/api/dashboards/db',
                            data=dashboard_source_body,
                            headers={"Content-type": "application/json", 
                                     "Accept": "application/json",
                                     "Authorization": "Bearer %s" % (key)})
    if not response.ok:
        print("Request to add Dashboard failed:", response.json()[0]['message'])
    return response.json()['url']