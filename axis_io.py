import requests
from requests.auth import HTTPDigestAuth
import time
from urllib3.exceptions import InsecureRequestWarning
import re

# Disable SSL warning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

class Axis233DIO:
    def __init__(self, ip_address, username, password, http_port=80, https_port=443):
        self.ip_address = ip_address
        self.auth_basic = requests.auth.HTTPBasicAuth(username, password)
        self.auth_digest = requests.auth.HTTPDigestAuth(username, password)
        self.auth = self.auth_digest
        self.connected = False
        self.protocol = None
        self.base_url = None
        self.http_port = http_port
        self.https_port = https_port
        self.protocols = ['http', 'https']
        self.session = requests.Session()
        self.session.verify = False
        self.session.auth = self.auth_basic

        # IO endpoints
        self.io_endpoints = {
            'input': '/axis-cgi/operator/param.cgi?action=list&group=root.Input',
            'output': '/axis-cgi/admin/param.cgi?action=update&root.Output.O',
            'port': '/axis-cgi/operator/param.cgi?action=list&group=root.Output',
            'status': '/axis-cgi/operator/param.cgi?action=list&group=root.Input'
        }

        # State mapping
        self.state_map = {
            'open': 'ON',
            'closed': 'OFF',
            True: 'ON',
            False: 'OFF'
        }

    def test_connection(self):
        """Test connection with auth fallback"""
        for protocol in self.protocols:
            port = self.https_port if protocol == 'https' else self.http_port
            base = f"{protocol}://{self.ip_address}:{port}"
            
            try:
                r = requests.get(base, timeout=5, verify=False)
                if r.status_code != 200:
                    continue
                
                # Try authentication methods
                for auth_method in [self.auth_digest, self.auth_basic]:
                    test_url = f"{base}/axis-cgi/operator/param.cgi"
                    try:
                        response = requests.get(test_url, auth=auth_method, timeout=5, verify=False)
                        if response.status_code == 200:
                            self.protocol = protocol
                            self.base_url = base
                            self.auth = auth_method
                            self.session.auth = auth_method
                            self.connected = True
                            return True
                    except:
                        continue
                            
            except requests.exceptions.RequestException:
                continue
                
        return False

    def get_input_state(self, port_number):
        """Read input state"""
        if not self.connected:
            return None
            
        try:
            port_idx = port_number - 1
            url = f"{self.base_url}{self.io_endpoints['input']}.I{port_idx}.Trig"
            response = self.session.get(url, auth=self.auth, timeout=5)
            
            if response.status_code == 200:
                return "open" in response.text.lower()
            
            return None
            
        except requests.exceptions.RequestException:
            return None

    def set_output_state(self, port_number, state):
        """Set output state"""
        if not self.connected:
            return False
            
        try:
            port_idx = port_number - 1
            state_val = "open" if state else "closed"
            
            paths = [
                f"/axis-cgi/admin/param.cgi?action=update&root.Output.O{port_idx}.Active={state_val}",
                f"/axis-cgi/io/output.cgi?action={state_val}&output={port_number}",
                f"/axis-cgi/admin/io.cgi?action=set&output={port_number}&value={'1' if state else '0'}"
            ]
            
            for path in paths:
                url = f"{self.base_url}{path}"
                response = self.session.get(url, timeout=5)
                
                if response.status_code == 200 and "OK" in response.text:
                    return True
                    
            return False

        except requests.exceptions.RequestException:
            return False

    def get_all_ports(self):
        """Get the state of all I/O ports"""
        if not self.connected:
            return None
            
        try:
            input_url = f"{self.base_url}{self.io_endpoints['status']}"
            input_response = self.session.get(input_url, auth=self.auth, timeout=5)
            
            output_url = f"{self.base_url}{self.io_endpoints['port']}"
            output_response = self.session.get(output_url, auth=self.auth, timeout=5)
            
            status = []
            if input_response.status_code == 200:
                for line in input_response.text.strip().split('\n'):
                    if "Trig=" in line:
                        port_num = int(line.split('.')[2][1]) + 1
                        state = line.split('=')[1].strip()
                        status.append(f"Input {port_num}: {self.state_map[state == 'open']}")
                    
            if output_response.status_code == 200:
                for line in output_response.text.strip().split('\n'):
                    if "Active=" in line:
                        port_num = int(line.split('.')[2][1]) + 1
                        state = line.split('=')[1].strip()
                        status.append(f"Output {port_num}: {self.state_map[state == 'open']}")
                        
            return "\n".join(status) if status else None
                
        except requests.exceptions.RequestException:
            return None
