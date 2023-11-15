import pexpect
import paramiko
import difflib

def get_running_config(ip, username, password, enable_password):
    # Create an SSH client
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # Connect to the device
    ssh.connect(ip, username=username, password=password)

    # Start an interactive shell
    shell = ssh.invoke_shell()

    # Enter enable mode
    shell.send("enable\n")
    shell.send(enable_password + "\n")

    # Get the running configuration
    shell.send("terminal length 0\n")
    shell.send("show running-config\n")
    output = ""
    while not output.endswith("#"):
        output += shell.recv(1024).decode("utf-8")

    # Close the SSH connection
    ssh.close()

    return output

def compare_configs(config1, config2):
    # Split the configurations into lines
    lines1 = config1.splitlines()
    lines2 = config2.splitlines()

    # Compare the configurations line by line
    diff = []
    for line in difflib.unified_diff(lines1, lines2):
        diff.append(line)

    return '\n'.join(diff)

# ... (Your existing code)
# Define variables
ip_address = '192.168.56.101'
username = 'cisco'
password = 'cisco123!'
password_enable = 'class123!'

# Create Telnet session
session = pexpect.spawn('telnet ' + ip_address, encoding='utf-8', timeout=20)
result = session.expect(['Username: ', pexpect.TIMEOUT])

# Check for an error, if an error exists, then display the error and exit
if result != 0:
    print('---FAILURE! creating session for: ', ip_address)
    exit()

# Session is expecting a username, enter details
session.sendline(username)
result = session.expect(['Password:', pexpect.TIMEOUT])

# Check for an error, if an error exists, then display the error and exit
if result != 0:
    print('---FAILURE! entering username: ', username)
    exit()

# Session is expecting a password, enter details
session.sendline(password)
result = session.expect(['#', pexpect.TIMEOUT])

# Check for an error, if it exists, then display the error and exit
if result != 0:
    print('---FAILURE! entering password: ', password)
    exit()

# Capture the running configuration
session.sendline('show running-config')
result = session.expect(['#', pexpect.TIMEOUT])

# Check for an error, if it exists, then display the error and exit
if result != 0:
    print('---FAILURE! capturing running configuration')

# Save the running configuration to a file locally
with open('running-config.txt', 'w') as config_file:
    config_file.write(session.before)

# Change hostname of router 

# Enter enable mode

session.sendline('enable')
result = session.expect(['Password:', pexpect.TIMEOUT, pexpect.EOF])

# CHECK FOR ERROR
if result != 0:
    print('FAILURE! entering enable mode')
    exit()

# Send enable password details
session.sendline(password_enable)
result = session.expect(['#', pexpect.TIMEOUT, pexpect.EOF])

# Check for an error
if result != 0:
    print('FAILURE! entering enable mode after sending the password')
    exit()

# Change to configuration mode on the router 
session.sendline('configure terminal')
result = session.expect([r'.\(config\)#', pexpect.TIMEOUT, pexpect.EOF])

#check for error
if result != 0:
    print('FAILURE! entering config mode')
    exit()

# Change the hostname to 'R1' 
session.sendline('hostname R1')
result = session.expect([r'R1\(config\)#', pexpect.TIMEOUT, pexpect.EOF])

#check for error
if result != 0:
    print('---FAILURE! setting hostname')

# Exit config mode 
session.sendline('exit')

# Exit enable mode 
session.sendline('exit')

# Display a success message if it works
print('------------------------------------------')
print('')
print('---Success! connecting to: ', ip_address)
print('---                username: ', username)
print('---                password: ', password)
print('')
print('------------------------------------------')

# Terminate Telnet to the device and close the session
session.sendline('quit')
###

# Get the running configuration after making changes
running_config_after_changes = get_running_config(ip_address, username, password, password_enable)

# Compare running and startup configurations
print("Running Configuration:\n", running_config_after_changes)
print("\nStartup Configuration:\n", startup_config)
print("\nDifferences between Running and Startup Configurations:\n", compare_configs(running_config_after_changes, startup_config))

# Compare running configuration with a local version (replace 'local_config.txt' with your file)
with open('local_config.txt', 'r') as local_file:
    local_config = local_file.read()
print("\nDifferences between Running Configuration and Local Version:\n", compare_configs(running_config_after_changes, local_config))
