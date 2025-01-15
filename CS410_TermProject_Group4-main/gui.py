
# there are a couple unused imports below that might be useful as we implement .. I left them for now
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QLineEdit,
    QPushButton,
    QFileDialog,
    QMessageBox,
    QCheckBox,
    QLabel,
    QTextEdit
)

import asyncio
import os
from qasync import QEventLoop, asyncSlot

# from PyQt5.QtCore import Qt, QFileInfo  # we can use this import for accessing files
from PyQt5.QtGui import QFont, QPixmap
import sys

import sftp_client as client

from sftp_client import connect_sftp, disconnect_sftp
from sftp_client import ls
from connection_storage import connection_info

#Styling variables
base_theme_style = "color: #ebfaff; background-color: #36452f;"
base_font = QFont("Helvetica", 12)
white_text = "color: #ebfaff;"

class QTextEditStream:
    def __init__(self):
        self.output = ""

    def write(self, text):
        # Append text to the QTextEdit widget
        self.output += text

    def flush(self):
        pass

class SftpGui(QWidget):
    def __init__(self):
        super().__init__()
        self.sftp = None
        self.ssh = None
        self.connected_host_name = ''
        self.init_ui()
        self.loop = QEventLoop(self)

    # create all the UI here and hide it / unhide it for use later
    def init_ui(self):
        self.create_main_window()
        self.create_login_ui()
        self.create_file_system_ui()
        self.hide_file_system_ui()
    
    # Stop the event loop when the window is closed
    def closeEvent(self, event):
        self.loop.stop()
        event.accept()

    def create_main_window(self):
        self.setWindowTitle("SFTP CLIENT")
        self.setGeometry(100, 100, 600, 600)
        self.setStyleSheet("background-color: #263337;")

    ##############################################################
    # File System Related Functions                              #
    ##############################################################
    
    def create_file_system_ui(self):
        # location format : x , y , width , height
        location = (200, 450, 300, 30)
        self.fs_status_label = self.create_label(location, base_font, white_text, "")

        # make file system display
        location = (100, 250, 150, 30)
        self.local_files_button = self.create_button(location, base_font, base_theme_style, "List Local Files")
        self.local_files_button.clicked.connect(self.list_local_files)

        # List remote files button
        location = (100, 300, 150, 30)
        self.remote_files_button = self.create_button(location, base_font, base_theme_style, "List Remote Files")
        self.remote_files_button.clicked.connect(self.list_remote_files)

        # make other stuff we need to do what we implemented in command line program
        location = (200, 350, 70, 30)
        self.logout_button = self.create_button(location, base_font, base_theme_style, "Logout")
        self.logout_button.clicked.connect(self.logout)
        return
    
    def hide_file_system_ui(self):
        # hide all the ui for created for file system .. for when we log out
        self.fs_status_label.hide()
        self.local_files_button.hide()
        self.remote_files_button.hide()
        self.logout_button.hide()
        return

    def show_file_system_ui(self):
        # if one of our file system ui items already exists just show..
        self.fs_status_label.setText(f"Connected to {self.connected_host_name}.")
        self.fs_status_label.show()
        self.local_files_button.show()
        self.remote_files_button.show()
        self.logout_button.show()
        return

    def hide_local_files_ui(self):
        self.back_button.hide()
        self.fs_status_label.hide()
        self.file_list_text.hide()
        self.show_file_system_ui()
        return
    
    def list_local_files(self):
        self.hide_file_system_ui()

        location = (200, 450, 300, 30)
        self.fs_status_label = self.create_label(location, base_font, white_text, "Listing local files...")
        self.fs_status_label.show()
        
        # Local file display window
        if not hasattr(self, 'file_list_text'):
            location = (100, 100, 400, 300)
            self.file_list_text = QTextEdit(self)
            self.file_list_text.setGeometry(*location)
            self.file_list_text.setReadOnly(True)
            self.file_list_text.show()

        else:
            self.file_list_text.show()
            
        #Store original stdout
        original_stdout = sys.stdout

        #Change stdout to custom widget
        sys.stdout = QTextEditStream()

        client.ls(client=os, args="-a", path='.')

        output_list = sys.stdout.output.split('\n')
        cleaned_output = "\n".join(output_list).replace('\n', '<br>')

        #Formatted string that controls the html styling
        styled_output = f"<span style='color: white; font-size: 16pt;'>{cleaned_output}</span>"

        self.file_list_text.setHtml(styled_output)

        #Reset back to original stdout
        sys.stdout = original_stdout

        location = (400, 400, 70, 30)
        self.back_button = self.create_button(location, base_font, base_theme_style, "Back")
        self.back_button.show()
        self.back_button.clicked.connect(self.hide_local_files_ui)
        return
    
    def list_remote_files(self):
        self.hide_file_system_ui()

        location = (200, 450, 300, 30)
        self.fs_status_label = self.create_label(location, base_font, white_text, "Listing remote files...")
        self.fs_status_label.show()
        
        # Local file display window
        if not hasattr(self, 'file_list_text'):
            location = (100, 100, 400, 300)
            self.file_list_text = QTextEdit(self)
            self.file_list_text.setGeometry(*location)
            self.file_list_text.setReadOnly(True)
            self.file_list_text.show()

        else:
            self.file_list_text.show()
            
        #Store original stdout
        original_stdout = sys.stdout

        #Change stdout to custom widget
        sys.stdout = QTextEditStream()

        client.ls(client=self.sftp, args="-a", path='.')

        output_list = sys.stdout.output.split('\n')
        cleaned_output = "\n".join(output_list).replace('\n', '<br>')

        #Formatted string that controls the html styling
        styled_output = f"<span style='color: white; font-size: 16pt;'>{cleaned_output}</span>"

        self.file_list_text.setHtml(styled_output)

        #Reset back to original stdout
        sys.stdout = original_stdout

        location = (400, 400, 70, 30)
        self.back_button = self.create_button(location, base_font, base_theme_style, "Back")
        self.back_button.show()
        self.back_button.clicked.connect(self.hide_local_files_ui)
        return
        
    def logout(self):
        client.disconnect_sftp(self.sftp)
        self.hide_file_system_ui()
        self.show_login_ui()
        print('Logging out.')

    # New Features for Managing Connections

    def show_new_connection_ui(self):
        self.hide_login_ui()

        location = (250, 50, 200, 30)
        self.new_username_entry = self.create_entry(location, base_font, base_theme_style, "New Username")
        
        location = (250, 100, 200, 30)
        self.new_password_entry = self.create_entry(location, base_font, base_theme_style, "New Password", True)

        location = (250, 150, 200, 30)
        self.new_server_entry = self.create_entry(location, base_font, base_theme_style, "New Server")

        location = (250, 200, 200, 30)
        self.save_new_connection_button = self.create_button(location, base_font, base_theme_style, "Save Connection")
        self.save_new_connection_button.clicked.connect(self.save_new_connection)

        location = (250, 250, 120, 30)
        self.cancel_new_connection_button = self.create_button(location, base_font, base_theme_style, "Cancel")
        self.cancel_new_connection_button.clicked.connect(self.cancel_new_connection_ui)

    # GUI - create new saved connection
    def save_new_connection(self):
        username = self.new_username_entry.text()
        password = self.new_password_entry.text()
        server = self.new_server_entry.text()
        alias = self.new_server_entry.text()

        connection_info.store_new_connection(alias, server, username, password)
        QMessageBox.information(self, "Success", "New connection saved successfully.")
        self.cancel_new_connection_ui()
    
    # Cancel create new saved connection
    def cancel_new_connection_ui(self):
        self.new_username_entry.hide()
        self.new_password_entry.hide()
        self.new_server_entry.hide()
        self.save_new_connection_button.hide()
        self.cancel_new_connection_button.hide()
        self.show_login_ui()

    # GUI - list saved connections
    def show_list_connections_ui(self):
        self.hide_login_ui()

        location = (100, 50, 400, 400)
        self.connections_list = QTextEdit(self)
        self.connections_list.setGeometry(*location)
        self.connections_list.setReadOnly(True)

        connections = connection_info.list_available_connection_names()
        display_text = ""

        for alias in connections:
            conn_info = connection_info.get_connection_by_alias(alias)
            if conn_info:
                display_text += f"Alias: {alias}\n"
                display_text += f"Server: {conn_info.get('hostname', 'Not Available')}\n"
                display_text += f"Username: {conn_info.get('username', 'Not Available')}\n\n"

        self.connections_list.setText(display_text)
        self.connections_list.show()

        location = (250, 450, 120, 30)
        self.back_from_list_button = self.create_button(location, base_font, base_theme_style, "Back")
        self.back_from_list_button.clicked.connect(self.cancel_list_connections_ui)

    # Cancel list saved connections
    def cancel_list_connections_ui(self):
        self.connections_list.hide()
        self.back_from_list_button.hide()
        self.show_login_ui()

    # GUI - edit saved connection
    def show_edit_connection_ui(self):
        self.hide_login_ui()

        location = (250, 50, 200, 30)
        self.edit_server_entry = self.create_entry(location, base_font, base_theme_style, "Server to Edit")

        location = (250, 100, 200, 30)
        self.edit_username_entry = self.create_entry(location, base_font, base_theme_style, "New Username")

        location = (250, 150, 200, 30)
        self.edit_password_entry = self.create_entry(location, base_font, base_theme_style, "New Password", True)

        location = (250, 200, 200, 30)
        self.save_edit_button = self.create_button(location, base_font, base_theme_style, "Save Changes")
        self.save_edit_button.clicked.connect(self.save_edited_connection)

        location = (250, 250, 200, 30)
        self.cancel_edit_button = self.create_button(location, base_font, base_theme_style, "Cancel")
        self.cancel_edit_button.clicked.connect(self.cancel_edit_connection_ui)

    # Saving updates.
    def save_edited_connection(self):
        alias = self.edit_server_entry.text()
        server = self.edit_server_entry.text()
        username = self.edit_username_entry.text()
        password = self.edit_password_entry.text()

        if connection_info.edit_connection(alias, server, username, password):
            QMessageBox.information(self, "Success", "Connection updated successfully.")
        else:
            QMessageBox.warning(self, "Error", "Failed to update connection. Check if the server exists.")

        self.cancel_edit_connection_ui()

    # Cancel edit saved connection
    def cancel_edit_connection_ui(self):
        self.edit_server_entry.hide()
        self.edit_username_entry.hide()
        self.edit_password_entry.hide()
        self.save_edit_button.hide()
        self.cancel_edit_button.hide()
        self.show_login_ui()

    ##############################################################
    # Login Related Functions                                    #
    ##############################################################

    def create_login_ui(self):
        # location format : x , y , width , height
        location = (250, 50, 120, 30)
        self.login_username_entry = self.create_entry(location, base_font, base_theme_style, "Username")
        
        location = (250, 100, 120, 30)
        self.login_password_entry = self.create_entry(location, base_font, base_theme_style, "Password", True)

        location = (250, 150, 120, 30)
        self.login_server_entry = self.create_entry(location, base_font, base_theme_style, "Server")

        location = (250, 200, 70, 30)
        self.login_button = self.create_button(location, base_font, base_theme_style, "Login")#, self.attempt_login)
        self.login_button.clicked.connect(self.attempt_login)

        location = (200, 250, 500, 30)
        self.login_status_label = self.create_label(location, base_font, white_text, "")
    
        # New Buttons for Managing Connections
        location = (250, 300, 300, 30)
        self.new_connection_button = self.create_button(location, base_font, base_theme_style, "Create New Connection")
        self.new_connection_button.clicked.connect(self.show_new_connection_ui)

        location = (250, 350, 300, 30)
        self.list_connections_button = self.create_button(location, base_font, base_theme_style, "List Saved Connections")
        self.list_connections_button.clicked.connect(self.show_list_connections_ui)

        location = (250, 400, 300, 30)
        self.edit_connection_button = self.create_button(location, base_font, base_theme_style, "Edit Saved Connection")
        self.edit_connection_button.clicked.connect(self.show_edit_connection_ui)

    @asyncSlot()
    async def attempt_login(self):
        self.login_status_label.setText("Connecting...")
        self.login_button.setDisabled(True)
        hostname = self.login_server_entry.text()
        username = self.login_username_entry.text()
        password = self.login_password_entry.text()

        success = await self.connect_sftp(hostname, username, password)
        self.login_button.setEnabled(True)
        if success:
            self.hide_login_ui()
            self.login_status_label.setText("Login Successful!")
            self.connected_host_name = hostname
            self.show_file_system_ui()
        else:
            self.login_status_label.setText("Login Failed, Please try again.")

    async def connect_sftp(self, hostname, username, password):
        loop = asyncio.get_event_loop()
        sftp, ssh = await loop.run_in_executor(None, connect_sftp, hostname, username, password)
        self.sftp = sftp
        self.ssh = ssh
        return sftp is not None
    
    # hide the login ui
    def hide_login_ui(self):
        self.login_password_entry.hide()
        self.login_server_entry.hide()
        self.login_username_entry.hide()
        self.login_button.hide()
        self.login_status_label.hide()
        self.new_connection_button.hide()
        self.list_connections_button.hide()
        self.edit_connection_button.hide()

    # show the login ui
    def show_login_ui(self):
        self.login_password_entry.show()
        self.login_server_entry.show()
        self.login_username_entry.show()
        self.login_button.show()
        self.login_status_label.setText("")
        self.login_status_label.show()
        self.new_connection_button.show()
        self.list_connections_button.show()
        self.edit_connection_button.show()

    ##############################################################
    # Create UI functions                                        #
    ##############################################################

    # create a button and then return the reference to that button
    def create_button(self, geometry, font, style, text, command=None):
        created_button = QPushButton(text, self)
        created_button.setGeometry(geometry[0], geometry[1], geometry[2], geometry[3])
        created_button.setFont(font)
        created_button.setStyleSheet(style)
        if command:
            created_button.clicked.connect(command)
        created_button.show()
        return created_button

    # create a button and then return the reference to that button
    # is_password and command are optional arguments
    def create_entry(self, geometry, font, style, text, is_password = False, command = None):
        created_entry = QLineEdit(self)
        created_entry.setPlaceholderText(text)
        created_entry.setGeometry(geometry[0], geometry[1], geometry[2], geometry[3])
        created_entry.setFont(font)
        created_entry.setStyleSheet(style)
        if is_password:
            created_entry.setEchoMode(QLineEdit.Password)
        if(command != None):
            created_entry.textChanged.connect(command)
        created_entry.show()
        return created_entry
    
    # create a label
    def create_label(self, geometry, font, style, text):
        label = QLabel(text, self)
        label.setGeometry(geometry[0], geometry[1], geometry[2], geometry[3])
        label.setFont(font)
        label.setStyleSheet(style)
        label.show()
        return label
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SftpGui()
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)
    window.show()

    gui = SftpGui()
    gui.show()

    with loop: # this is needed for async events so we can communicate to the sftp server and still have the ui work.
        loop.run_forever()
