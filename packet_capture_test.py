"""
This code is made for execute the command tcpdump on interfaces WAN,LAN,OPNVPN of the pfSenses firewalls
The script needs a gpg file that contains the passwords of admin accounts of firewalls to execute the tcpdump command
The dumps are downloaded on local folder with the name of router and name of the interface
"""

import gnupg
import json
from getpass import getpass
import paramiko
import toml
from datetime import datetime
from scp import SCPClient
import threading
import time

def decrypt_gpg_file(file_path, gpg_home_path):
    gpg = gnupg.GPG(gnupghome=gpg_home_path)
    with open(file_path, 'rb') as f:
        passphrase = getpass()
        decrypted_data = gpg.decrypt_file(f, passphrase=passphrase, output=None, always_trust=True)
    return decrypted_data.data.decode('utf-8')


def parse_json_data(json_string):
    return json.loads(json_string)


def tcpdump(name,ip,password):
    password = password
    host = ip
    port = 8022
    username = "admin"
    now = str(datetime.today()).replace(" ", "_").split(".")[0]
    try:
        # Create an SSH client instance
        ssh_client = paramiko.SSHClient()
        # Automatically add the server's host key (this is insecure, use it only for testing purposes)
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        # Connect to the remote server
        ssh_client.connect(hostname=host, port=port, username=username, password=password)
        timer = 300

        # Create igb0 folder
        command = f'mkdir /home/alban/igb0'
        stdin, stdout, stderr = ssh_client.exec_command(command)
        # Create igb1 folder
        command = f'mkdir /home/alban/igb1'
        stdin, stdout, stderr = ssh_client.exec_command(command)
        
        # Execute a tcpdump command remotely on interface igb0
        command = f'tcpdump -G {timer} -W 1 -i igb0 -w /home/alban/igb0/"{name}"_igb0_"{now}".pcap'
        stdin, stdout, stderr = ssh_client.exec_command(command)
        # Execute a tcpdump command remotely on interface igb1
        command = f'tcpdump -G {timer} -W 1 -i igb1 -c 100 -w /home/alban/igb1/"{name}"_igb1_"{now}".pcap'
        stdin, stdout, stderr = ssh_client.exec_command(command)

        time.sleep(timer + 30)

        #copy the pcaps file from remote to local machine
        scp = SCPClient(ssh_client.get_transport())
        scp.get(f'/home/alban/igb1', f'/home/alban/PacketsCaptures/{name}/', recursive=True)
        scp.get(f'/home/alban/igb0', f'/home/alban/PacketsCaptures/{name}/', recursive=True)
        scp.close()

        # Remove igb0 folder
        command = f'rm -fr /home/alban/igb0'
        stdin, stdout, stderr = ssh_client.exec_command(command)
        # Remove igb1 folder
        command = f'rm -fr /home/alban/igb1'
        stdin, stdout, stderr = ssh_client.exec_command(command)
        
        # Close the SSH connection
        ssh_client.close()
    except paramiko.AuthenticationException:
        print("Authentication failed. Please check your credentials.")
    except paramiko.SSHException as e:
        print(f"SSH error: {e}")
    except paramiko.BadHostKeyException as e:
        print(f"Host key error: {e}")
    except Exception as e:
        print(f"Error: {e}")


def scp(name,ip,password):
    password = password
    host = ip
    port = 8022
    username = "admin"
    try:
        # Create an SSH client instance
        ssh_client = paramiko.SSHClient()
        # Automatically add the server's host key (this is insecure, use it only for testing purposes)
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        # Connect to the remote server
        ssh_client.connect(hostname=host, port=port, username=username, password=password)
        #copy the pcaps file from remote to local machine
        scp = SCPClient(ssh_client.get_transport())
        scp.get(f'/home/alban/igb1', f'/home/alban/PacketsCaptures/{name}/', recursive=True)
        scp.get(f'/home/alban/igb0', f'/home/alban/PacketsCaptures/{name}/', recursive=True)
        scp.close()

        # Remove igb0 folder
        command = f'rm -fr /home/alban/igb0'
        stdin, stdout, stderr = ssh_client.exec_command(command)
        # Remove igb1 folder
        command = f'rm -fr /home/alban/igb1'
        stdin, stdout, stderr = ssh_client.exec_command(command)
        
        # Close the SSH connection
        ssh_client.close()
    except paramiko.AuthenticationException:
        print("Authentication failed. Please check your credentials.")
    except paramiko.SSHException as e:
        print(f"SSH error: {e}")
    except paramiko.BadHostKeyException as e:
        print(f"Host key error: {e}")
    except Exception as e:
        print(f"Error: {e}")


def loop(passwd, config_file_data):
    start = time.perf_counter()
    routers = config_file_data['routers']
    threads = []
    for router in routers:
        t = threading.Thread(target=tcpdump, args=(router, routers[router], passwd[router]))
        t.start()
    time.sleep(330)
    for router in routers:
        t = threading.Thread(target=scp, args=(router, routers[router], passwd[router]))
        t.start()
    for thread in threads:
        thread.join()
    finish = time.perf_counter()
    print(f'Finished in {round(finish-start, 2)} second(s)')
    
        
def main():
    config_file = "./config.toml"
    config_file_data = toml.load(config_file)
    file_path = "/home/alban/ADMINS_PASSWD.json.gpg"
    gpg_home_path = "/home/alban/.gnupg"
    decrypted_json_string = decrypt_gpg_file(file_path, gpg_home_path)
    decrypted_data_dict = parse_json_data(decrypted_json_string)
    print(loop(decrypted_data_dict, config_file_data))

if __name__ == '__main__':
    main()