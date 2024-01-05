import paramiko
from scp import SCPClient
import os


def main(name,
         ip,
         port,
         username,
         password,
         output,
         interface):
    try:
        # Create an SSH client instance
        ssh_client = paramiko.SSHClient()
        # Automatically add the server's host key (this is insecure, use it only for testing purposes)
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        # Connect to the remote server
        ssh_client.connect(hostname=ip,
                           port=port,
                           username=username,
                           password=password)
        # copy the pcaps file from remote to local machine
        scp = SCPClient(ssh_client.get_transport())
        if os.path.isdir(f"{output}{name}/{interface}"):
            print("Folder already exist")
        else:
            os.makedirs(f"{output}{name}/{interface}", exist_ok=True)
        print(f".pcap files of interface {interface} will be copied in {output}{name}/{interface}")
        scp.get(f'/tmp/packet-capture/{interface}/',
                f'{output}{name}/',
                recursive=True)
        scp.close()

        # Remove interface folder files
        command = 'rm -rf /tmp/packet-capture'
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