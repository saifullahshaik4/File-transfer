import json
import keyring
import os

class ConnectionManager:
    def __init__(self, service_name, alias_list_file):
        self.service_name = service_name
        self.alias_list_file = alias_list_file
        self._ensure_alias_list_file_exists()

    # Ensure the alias list file exists
    def _ensure_alias_list_file_exists(self):
        if not os.path.exists(self.alias_list_file):
            with open(self.alias_list_file, 'w') as file:
                json.dump([], file)

    # Get the alias list from the file.
    def _get_alias_list(self):
        with open(self.alias_list_file, 'r') as file:
            return json.load(file)

    # Save the alias list to the file.
    def _save_alias_list(self, alias_list):
        with open(self.alias_list_file, 'w') as file:
            json.dump(alias_list, file)

    # Store the connection information as a JSON string in the keyring
    def store_new_connection(self, alias, hostname, username, password):
        connection_info = json.dumps({'hostname': hostname, 'username': username, 'password': password})
        keyring.set_password(self.service_name, alias, connection_info)

        # Update the alias list
        alias_list = self._get_alias_list()
        if alias not in alias_list:
            alias_list.append(alias)
            self._save_alias_list(alias_list)

    # List all available connection names (aliases) stored in the keyring
    def list_available_connection_names(self):
        return self._get_alias_list()
    
    # List all available connection names (aliases) stored in the keyring
    def get_connection_by_alias(self, alias):
        connection_info_json = keyring.get_keyring().get_password(self.service_name, alias)
        if connection_info_json:
            return json.loads(connection_info_json)
        else:
            return None
        
    # Edit an existing connection by alias
    def edit_connection(self, alias, new_hostname=None, new_username=None, new_password=None):
        connection_info = self.get_connection_by_alias(alias)
        if connection_info:
            if new_hostname:
                connection_info['hostname'] = new_hostname
            if new_username:
                connection_info['username'] = new_username
            if new_password:
                connection_info['password'] = new_password

            # Store the updated connection info
            self.store_new_connection(alias, connection_info['hostname'], connection_info['username'], connection_info['password'])
            return True
        else:
            return False

connection_info = ConnectionManager('sftp_connection_service', 'aliases.json')
