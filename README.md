# packet_capture
Tool to use tcpdump command on remote for every interfaces, get the pcap file on local with scp

packet-capture will ask for some parmaters:
    --hostip TEXT    The ip address of the remote host
    --hostname TEXT  The name of the remote host
    --port TEXT      The ssh port on remote
    --hosts TEXT     The file that contains the list of hosts in hosts.toml
    --user TEXT      The user to make a ssh connection on remote
    --passwd TEXT    The password of user
    --passwds TEXT   The passwords.gpg file to use that contains passwords for ssh connection

For one remote only :
    Use the options
For multiple remote:
    Make sure that the username you will use is the same on each remote
    Use the option --passwds to specify a .json.gpg file that contains passwords like in the example file
    Make sure that you have a ~/.gnpug folder to decrypt the .gpg files


To decrypt the example file you have to use the command > gpg -d /path/to/example_file
And enter the key 'toto'

You must have a ~/.gnupg folder
