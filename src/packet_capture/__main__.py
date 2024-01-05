"""
This code is made for execute the command tcpdump on interfaces WAN,LAN,OPNVPN of the pfSenses firewalls
The script needs a gpg file that contains the passwords of admin accounts of firewalls to execute the tcpdump command
The dumps are downloaded on local folder with the name of router and name of the interface
"""

import pyfiglet
import gnupg
import json
from getpass import getpass
import toml
import threading
from packet_capture.tcpdump import tcpdump as tcpdump
import click


def print_large_text(text):
    ascii_banner = pyfiglet.figlet_format(text, font="big")
    print(ascii_banner)


def decrypt_gpg_file(file_path, gpg_home_path):
    gpg = gnupg.GPG(gnupghome=gpg_home_path)
    with open(file_path, 'rb') as f:
        passphrase = getpass(prompt="gpg key to decrypt .json.gpg file :")
        decrypted_data = gpg.decrypt_file(f, 
                                          passphrase=passphrase, 
                                          output=None, 
                                          always_trust=True)
    return decrypted_data.data.decode('utf-8')


def parse_json_data(json_string):
    return json.loads(json_string)


@click.command()
@click.option('--hostip', 
              default=None, 
              help='The ip address of the remote host')
@click.option('--hostname', 
              default=None, 
              help='The name of the remote host')
@click.option('--port', 
              default=22, 
              help='The ssh port on remote',)
@click.option('--hosts', 
              default=None, 
              help='The file that contains the list of hosts in hosts.toml')
@click.option('--user', 
              default=None, 
              help='The user to make a ssh connection on remote')
@click.option('--passwd', 
              default=None, 
              help='The passwd of user')     
@click.option('--passwds', 
              default=None, 
              help='The passwd.gpg file to for ssh connection')  
@click.option('--gnupg', 
              default=None, 
              help='The path to .gnupg folder to decrypt .json.gpg file')
@click.option('--output', 
              default=None, 
              help='/path/to/folder that will contain .pcap files') 
def main(hostip, 
         hostname, 
         port, 
         hosts, 
         user, 
         passwd, 
         passwds, 
         gnupg, 
         output):
    print_large_text("Packet Capture")
    print("tcpdump command will be executed, use --help for options")
    if hostip is not None and hosts is None:
        tcpdump(name=hostname, 
                ip=hostip, 
                password=passwd, 
                username=user, 
                port=port, 
                output=output)
    elif hostip is None and hosts is not None:
        hosts_data = toml.load(hosts)['routers']
        file_path = passwds
        gpg_home_path = gnupg
        print(file_path)
        decrypted_json_string = decrypt_gpg_file(file_path, gpg_home_path)
        decrypted_data_dict = parse_json_data(decrypted_json_string)
        for data in hosts_data:
            print(f"tcpdump will be executed on {hosts_data[data]}")
            threads = []
            t1 = threading.Thread(target=tcpdump, 
                                  args=(data,
                                        hosts_data[data],
                                        decrypted_data_dict[data],
                                        user,
                                        port,
                                        output))
            t1.start()
        for thread in threads:
            thread.join()


if __name__ == '__main__':
    main()