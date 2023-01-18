import xml.etree.ElementTree as ET
from flask import Flask, render_template, url_for, flash, redirect, request
import re
import subprocess

app = Flask(__name__)

@app.route('/api/block_ip/<ip_address>', methods=['POST'])
def block_ip(ip_address):

    tree = ET.parse('web.config')
    root = tree.getroot()

    parent_element = root.find(".//system.webServer//security//ipSecurity")

    child = parent_element.find(f"add[@ipAddress='{ip_address}'][@allowed='false']")

    if child is None:
        new_element = ET.Element("add")
        new_element.set("ipAddress", ip_address)
        new_element.set("allowed", "false")

        parent_element.append(new_element)

    tree.write('web.config')

    return f'IP Address {ip_address} had been blocked in IIS'

@app.route('/webhook', methods=['POST'])
def webhook():
    if request.method == "POST":
        result = request.json
        event = result["result"]["_raw"]
        event_sections = event.split(":")[2:]

        ip_address = ""

        for section in event_sections:
            match = re.search(r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?).){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b', section)

            if match:
                ip_address = match.group()
                print(ip_address)

        if ip_address is None:
            print("No ip address found")
        else:
            url = f"http://localhost:3000/api/block_ip/{ip_address}"
            process = subprocess.run(["curl", "-X", "POST", url], capture_output=True)

    return 'Alert received'

if __name__ == '__main__':
    app.run(debug=True, port=3000)