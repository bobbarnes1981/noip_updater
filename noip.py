import base64
import configparser
import http.client
import json
import sys
import urllib.parse

client_name = 'RobertBarnesNoIpUpdater'
client_version = '0.0.1'
client_email = 'robertbarnes1981@googlemail.com'

print(client_name)
print(client_version)

messages = {
    'good': [True, 'DNS hostname update successful.'],
    'nochg': [True, 'IP address is current, no update performed.'],
    'nohost': [False, 'Hostname supplied does not exist under specified account.'],
    'badauth': [False, 'Invalid username password combination.'],
    'badagent': [False, 'Client disabled.'],
    '!donator': [False, 'An update request was sent including a feature that is not available to the specified user.'],
    'abuse': [False, 'Username is blocked due to abuse. Either for not following our update specifications or disabled due to violation of the No-IP terms of service.'],
    '911': [False, 'A fatal error on our side such as a database outage. Retry the update no sooner than 30 minutes.']
}

# https://bugs.gentoo.org/show_bug.cgi?id=261194

if len(sys.argv) > 1:
    config_file = sys.argv[1]
else:
    print('using default config file')
    config_file = 'noip.conf'
print('config file: %s' % config_file)

config = configparser.ConfigParser()
config.read(config_file)

myip = None

# get ip

get_ip_url = 'api.ipify.org'

print('getting ip from: %s' % get_ip_url)

get_ip_path = '/?format=json'

connection = http.client.HTTPSConnection(get_ip_url);
connection.request('GET', get_ip_path)
response = connection.getresponse()

print(response.status)

if response.status == http.client.OK:
    data = json.loads(response.readall().decode('ascii'))
    print(data)

    myip = data['ip']

# update noip

if myip != None:

    set_ip_url = 'dynupdate.no-ip.com'

    print('setting ip at: %s' % set_ip_url)

    username = config.get('noip', 'username')
    password = config.get('noip', 'password')
    hostname = config.get('noip', 'hostname')

    authorization = base64.b64encode('{username}:{password}'.format(username = username, password = password).encode('ascii')).decode('ascii')

    user_agent = '{client_name}/{client_version} {client_email}'.format(client_name = client_name, client_version = client_version, client_email = client_email)

    headers = {'User-Agent': user_agent, 'Authorization': 'Basic {authorization}'.format(authorization = authorization)}

    set_ip_path = '/nic/update?hostname={hostname}&myip={myip}'.format(hostname = hostname, myip = myip)

    connection = http.client.HTTPSConnection(set_ip_url)
    connection.request('GET', set_ip_path, {}, headers)
    response = connection.getresponse()

    print(response.status)

    if response.status == http.client.OK:
        data = response.readall().decode('ascii')
        print(data)
    
        parts = data.split()
        
        result = messages[parts[0]]

        if result[0] == True:
            print('SUCCESS %s' % parts[1])
        else:
            print('FAILED')
        print(result[1])

