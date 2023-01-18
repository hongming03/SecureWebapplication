import xml.etree.ElementTree as ET

ipaddress = "123.123.123.123"

tree = ET.parse('test.config')
root = tree.getroot()

parent_element = root.find(".//system.webServer//security//ipSecurity")

new_element = ET.Element("add")
new_element.set("ipAddress", ipaddress)
new_element.set("allowed", "false")

parent_element.append(new_element)

tree.write('test.config')