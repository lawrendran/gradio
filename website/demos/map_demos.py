import os, sys
import subprocess
from jinja2 import Template
import json
import re

GRADIO_DIR = os.path.join(os.getcwd(), os.pardir, os.pardir)
GRADIO_DEMO_DIR = os.path.join(GRADIO_DIR, "demo")
GRADIO_GUIDES_DIR = os.path.join(GRADIO_DIR, "guides")
sys.path.insert(0, GRADIO_DEMO_DIR)
DEMO_PATTERN = r'demos\["([A-Za-z0-9_]+)"]'
demos_to_run = []
for guide_filename in os.listdir(GRADIO_GUIDES_DIR):
    with open(os.path.join(GRADIO_GUIDES_DIR, guide_filename)) as guide_file:
        guide_content = guide_file.read()
    demos_to_run += re.findall(DEMO_PATTERN, guide_content)

demo_port_sets = []
for port, demo_name in enumerate(demos_to_run, start=7860):
    demo_folder = os.path.join(GRADIO_DEMO_DIR, demo_name)
    requirements_file = os.path.join(demo_folder, "requirements.txt")
    if os.path.exists(requirements_file):
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", requirements_file])
    setup_file = os.path.join(demo_folder, "setup.sh")
    if os.path.exists(setup_file):
        subprocess.check_call(["sh", setup_file])
    demo_port_sets.append((demo_name, port))
with open("nginx_template.conf") as nginx_template_conf: 
    template = Template(nginx_template_conf.read())
output_nginx_conf = template.render(demo_port_sets=demo_port_sets)
with open("nginx.conf", "w") as nginx_conf:
    nginx_conf.write(output_nginx_conf)
with open("demos.json", "w") as demos_file:
    json.dump(demo_port_sets, demos_file)