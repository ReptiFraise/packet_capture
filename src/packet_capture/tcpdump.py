"""
This code is made for execute the command tcpdump on interfaces WAN,LAN,OPNVPN of the pfSenses firewalls
The script needs a gpg file that contains the passwords of admin accounts of firewalls to execute the tcpdump command
The dumps are downloaded on local folder with the name of router and name of the interface
"""

import paramiko
from datetime import datetime
import threading
from packet_capture.sscp import main as sscp


def tcpdump(name,
            ip,
            password,
            username,
            port,
            output,
            timer):
    now = str(datetime.today()).replace(" ", "_").split(".")[0]
    try:
        # Create an SSH client instance
        ssh_client = paramiko.SSHClient()
        # Automatically add the server's host key
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        # Connect to the remote server
        ssh_client.connect(hostname=ip,
                           port=port,
                           username=username,
                           password=password)
        print(f"ssh on {ip}:{port} successfully connected")
        interfaces = []
        command = 'netstat -i'
        stdin, stdout, stderr = ssh_client.exec_command(command)
        lines = stdout.readlines()
        for line in lines:
            interface = line.split(" ")[0]
            interfaces.append(interface)
        interfaces.remove(interfaces[0])
        for interface in interfaces:
            while interfaces.count(interface) != 1:
                interfaces.remove(interface)
        
        for interface in interfaces:
            t = threading.Thread()
            t.start()
            # Create interface folder
            command = f'mkdir -p /tmp/packet-capture/{interface}/'
            stdin, stdout, stderr = ssh_client.exec_command(command)
            # Execute a tcpdump command remotely on interface
            if username != "admin" and username != "root":
                try:
                    print("tcpdump will be executed with sudo")
                    command = f'''echo {password} | sudo -S tcpdump -G {timer} -W 1 -i {interface} -w /tmp/packet-capture/{interface}/"{name}"_{interface}_"{now}".pcap'''
                    stdin, stdout, stderr = ssh_client.exec_command(command)
                except SystemError:
                    "Exec this command with sudo is impossible"
            else:
                command = f'tcpdump -G {timer} -W 1 -i {interface} -w /tmp/packet-capture/{interface}/"{name}"_{interface}_"{now}".pcap'
                stdin, stdout, stderr = ssh_client.exec_command(command)
            if stdout.channel.recv_exit_status() == 1:
                print(f"tcpdump can't be executed on interface {interface} on host {name}={ip}")
                pass
            else:
                print(f"tcpdump successfully executed on interface {interface} on host {name}={ip}")
            # Copy the folders from remote that contains .pcap files
                sscp(name=name,
                     ip=ip,
                     username=username,
                     password=password,
                     port=port,
                     output=output,
                     interface=interface)
        # Close the SSH connection """ """
        ssh_client.close()
    except paramiko.AuthenticationException:
        print("Authentication failed. Please check your credentials.")
    except paramiko.SSHException as e:
        print(f"SSH error: {e}")
    except paramiko.BadHostKeyException as e:
        print(f"Host key error: {e}")
    except Exception as e:
        print(f"Error: {e}")