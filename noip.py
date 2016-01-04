import base64
import configparser
import http.client
import json
import sys
import urllib.parse

messages = {
    'good': [True, 'DNS hostname update successful. Followed by a space and the IP address it was updated to.'],
    'nochg': [True, 'IP address is current, no update performed. Followed by a space and the IP address that it is currently set to.'],
    'nohost': [False, 'Hostname supplied does not exist under specified account, client exit and require user to enter new login credentials before performing an additional request.'],
    'badauth': [False, 'Invalid username password combination'],
    'badagent': [False, 'Client disabled. Client should exit and not perform any more updates without user intervention.'],
    '!donator': [False, 'An update request was sent including a feature that is not available to that particular user such as offline options.'],
    'abuse': [False, 'Username is blocked due to abuse. Either for not following our update specifications or disabled due to violation of the No-IP terms of service. Our terms of service can be viewed here. Client should stop sending updates.'],
    '911': [False, 'A fatal error on our side such as a database outage. Retry the update no sooner than 30 minutes.']
}

# https://bugs.gentoo.org/show_bug.cgi?id=261194

if len(sys.argv) > 1:
    config_file = sys.argv[1]
else:
    config_file = 'noip.conf'

config = configparser.ConfigParser()
config.read(config_file)

client_name = 'RobertBarnesNoIpUpdater'
client_version = '0.0.1'
client_email = 'robertbarnes1981@googlemail.com'

# get ip

connection = http.client.HTTPSConnection('api.ipify.org');
connection.request('GET', '/?format=json')
response = connection.getresponse()

myip = None

if response.status == http.client.OK:
    data = json.loads(response.readall().decode('ascii'))
    myip = data['ip']

# update noip

if myip != None:

    username = config.get('noip', 'username')
    password = config.get('noip', 'password')
    hostname = config.get('noip', 'hostname')

    authorization = base64.b64encode('{username}:{password}'.format(username = username, password = password).encode('ascii')).decode('ascii')

    user_agent = '{client_name}/{client_version} {client_email}'.format(client_name = client_name, client_version = client_version, client_email = client_email)

    headers = {'User-Agent': user_agent, 'Authorization': 'Basic {authorization}'.format(authorization = authorization)}

    url = '/nic/update?hostname={hostname}&myip={myip}'.format(hostname = hostname, myip = myip)

    connection = http.client.HTTPSConnection('dynupdate.no-ip.com')
    connection.request('GET', url, {}, headers)
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

