#!/usr/bin/python3

from pathlib import Path
from ftplib import FTP  # FTP_TLS

import imgkit
from jinja2 import Template


def get_data():
    import sunspec.core.client as client
    import sunspec.core.modbus as modbus
    try:
        d = client.SunSpecClientDevice(client.TCP, 126, ipaddr='192.168.0.170')
        # ipport=502, timeout=None, trace=False
        # device id: 3-SMA Modbus, 126-SunSpecModbus
        data = {}
        for x in d.models:
            # print('Model: {}'.format(x))
            d[x].read()
            tmp = {}
            for y in d[x].points:
                # print('Point: {}'.format(y))
                # print('{} = {}'.format(y, d[x][y]))
                tmp[y] = d[x][y]
                data[x] = tmp
    except modbus.client.ModbusClientError as e:
        print(f'Error while connecting to inverter: ${e}')
    return data


def get_mockup_data():
    import json
    with open('demo.json') as f:
        return json.load(f)


def upload_to_ftp(filename, host, user, password):
    file_path = Path(filename)
    with FTP(host, user, password) as ftp, open(file_path, 'rb') as file:
        ftp.storbinary(f'STOR {file_path.name}', file)


def upload_to_sftp(filename, host):
    cnopts = pysftp.CnOpts(knownhosts='./.ssh/known_hosts')
    # private_key_pass
    with pysftp.Connection(host=host, port=22, username='', private_key='./.ssh/id_rsa', cnopts=cnopts) as sftp:
        # username="root", password="password", log="./temp/pysftp.log"
        sftp.cd('temp')
        sftp.put(filename)


def create_html_from_template(template, data, output_file):
    power_overall = str(int(int(data['status']['ActWh'])/1000))
    output_data = {
        'temperature_outdoors': '42.5 °C',
        'temperature_module': '42.3 °C',
        'radiation': '42 lux',
        'current_dc': '42.2 A',
        'voltage_dc': '42 V',
        'power_dc': '42 W',
        'voltage_ac': '{} V'.format(data['inverter']['PhVphA']),
        'current_ac': '{} A'.format(data['inverter']['AphA']),
        'power_ac': '{} VA'.format(data['inverter']['VA']),
        'efficiency': '42 %',
        'power_overall': '{} kWh'.format(power_overall)
    }
    with open(template) as f:
        template = Template(f.read())
    with open(output_file, 'w') as f:
        f.write(template.render(output_data))


def main():
    html_output = './html/output.html'
    png_output = './html/output.png'
    create_html_from_template('./html/template.html', get_data(),
                              html_output)
    imgkit.from_file(html_output, png_output)
    # upload_to_ftp(png_output, 'localhost', 'user', 'pass')
    # upload_to_sftp(png_output, 'hostname')


main()
