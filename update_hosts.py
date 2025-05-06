import os
import sys
import ctypes
import platform

def is_admin():
    """Check if the script is running with admin privileges"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def update_hosts():
    """Update the hosts file with DeepSeek API IP mapping"""
    if platform.system() != 'Windows':
        print("This script is for Windows systems only.")
        return False
        
    if not is_admin():
        print("This script needs to be run with administrator privileges.")
        print("Please right-click and select 'Run as administrator'")
        return False
    
    hosts_path = r'C:\Windows\System32\drivers\etc\hosts'
    backup_path = r'C:\Windows\System32\drivers\etc\hosts.bak'
    
    # API endpoints and their IPs
    mappings = [
        ('api.deepseek.ai', '34.107.189.223'),
        ('api2.deepseek.ai', '52.58.133.175')
    ]
    
    try:
        # Create backup
        if os.path.exists(hosts_path):
            with open(hosts_path, 'r') as f:
                hosts_content = f.read()
            with open(backup_path, 'w') as f:
                f.write(hosts_content)
            print(f"Backup created at {backup_path}")
        
        # Read existing hosts file
        if os.path.exists(hosts_path):
            with open(hosts_path, 'r') as f:
                lines = f.readlines()
        else:
            lines = []
        
        # Remove any existing DeepSeek entries
        lines = [line for line in lines if not any(domain in line for domain, _ in mappings)]
        
        # Add new mappings
        lines.append("\n# DeepSeek API mappings\n")
        for domain, ip in mappings:
            lines.append(f"{ip}\t{domain}\n")
        
        # Write updated hosts file
        with open(hosts_path, 'w') as f:
            f.writelines(lines)
        
        print("Hosts file updated successfully!")
        print("\nAdded mappings:")
        for domain, ip in mappings:
            print(f"{ip} -> {domain}")
        
        # Flush DNS cache
        os.system('ipconfig /flushdns')
        print("\nDNS cache flushed.")
        return True
        
    except Exception as e:
        print(f"Error updating hosts file: {str(e)}")
        print("If backup exists, you can restore it from:", backup_path)
        return False

if __name__ == '__main__':
    if update_hosts():
        print("\nPlease try running test_api_connection.py again.")