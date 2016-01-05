import base64
import configparser
import http.client
import json
import sys
import urllib.parse

class Message(object):

    def __init__(self, success, description, exit_code):
        self.success = success
        self.description = description
        self.exit_code = exit_code

class Ipify(object):

    def __init__(self, url):
        self.url = url

    def get_ip(self):
        print('getting ip from: %s' % self.url)

        path = '/?format=json'

        connection = http.client.HTTPSConnection(self.url);
        connection.request('GET', path)
        response = connection.getresponse()

        print(response.status)

        if response.status == http.client.OK:
            data = json.loads(response.readall().decode('ascii'))
            print(data)
            return data['ip']

        return None

class Noip(object):

    client_name = 'RobertBarnesNoIpUpdater'
    client_version = '0.0.1'
    client_email = 'robertbarnes1981@googlemail.com'

    def __init__(self, url):
        self.messages = {
            'good': Message(True, 'DNS hostname update successful.', 0),
            'nochg': Message(True, 'IP address is current, no update performed.', 0),
            'nohost': Message(False, 'Hostname supplied does not exist under specified account.', 1),
            'badauth': Message(False, 'Invalid username password combination.', 2),
            'badagent': Message(False, 'Client disabled.', 3),
            '!donator': Message(False, 'An update request was sent including a feature that is not available to the specified user.', 4),
            'abuse': Message(False, 'Username is blocked due to abuse. Either for not following our update specifications or disabled due to violation of the No-IP terms of service.', 5),
            '911': Message(False, 'A fatal error on our side such as a database outage. Retry the update no sooner than 30 minutes.', 6)
        }

        self.url = url

    def update_ip(self, username, password, hsotname, ip):
        print('setting ip at: %s' % self.url)

        authorization = base64.b64encode('{username}:{password}'.format(username = username, password = password).encode('ascii')).decode('ascii')

        user_agent = '{client_name}/{client_version} {client_email}'.format(client_name = self.client_name, client_version = self.client_version, client_email = self.client_email)

        headers = {'User-Agent': user_agent, 'Authorization': 'Basic {authorization}'.format(authorization = authorization)}

        path = '/nic/update?hostname={hostname}&myip={myip}'.format(hostname = hostname, myip = myip)

        connection = http.client.HTTPSConnection(self.url)
        connection.request('GET', path, {}, headers)
        response = connection.getresponse()

        print(response.status)

        if response.status == http.client.OK:
            data = response.readall().decode('ascii')
            print(data)
    
            parts = data.split()
        
            return self.messages[parts[0]]

        return Message(False, 'Http Error %s' % response.status, 999)
        
print(Noip.client_name)
print(Noip.client_version)

# load config

if len(sys.argv) > 1:
    config_file = sys.argv[1]
else:
    print('using default config file')
    config_file = 'noip.conf'
print('config file: %s' % config_file)

config = configparser.ConfigParser()
config.read(config_file)

username = config.get('noip', 'username')
password = config.get('noip', 'password')
hostname = config.get('noip', 'hostname')

# get ip

myip = Ipify('api.ipify.org').get_ip()

# update noip

if myip == None:
    sys.exit(999)

message = Noip('dynupdate.no-ip.com').update_ip(username, password, hostname, myip)

if message.success == True:
    print('SUCCESS')
else:
    print('FAILED')

print(message.description)
sys.exit(message.exit_code)

