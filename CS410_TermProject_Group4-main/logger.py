import os
from datetime import datetime

class Logger:
    def __init__(self):
        super().__init__()
        self.default_path = os.path.join(os.getcwd(), 'Logs')
        if not os.path.exists(self.default_path):
            os.makedirs(self.default_path)
        self.update_log_file_name()

    def update_log_file_name(self):
        current_date = datetime.now().strftime('%m-%d-%Y')
        self.log_file = os.path.join(self.default_path, f'{current_date}_rolling_log.txt')

    def log_info(self, message):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_message = f'INFO | {timestamp} | {message}'
        self.write_to_file(self.log_file, log_message)
        return timestamp

    def log_warning(self, message):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_message = f'WARNING | {timestamp} | {message}'
        self.write_to_file(self.log_file, log_message)
        return timestamp

    def log_error(self, message):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_message = f'ERROR | {timestamp} | {message}'
        self.write_to_file(self.log_file, log_message)
        return timestamp

    def write_to_file(self, file_path, message):
        try:
            with open(file_path, 'a') as f:
                f.write(f'{message}\n')
        except Exception as e:
            print(e)
        return 0
    
    def contains_string(self, file_path, search_string):
        try:
            with open(file_path, 'r') as f:
                for line in f:
                    if search_string in line:
                        return True
        except Exception as e:
            print(e)
        return False

logger = Logger()
