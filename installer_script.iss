; Inno Setup Script for DuckDNS Connector

[Setup]
AppId={{1C7A8B3D-4F2E-4E9A-8B6C-9D0E1F2A3B4C}}
AppName=DuckDNS Connector
AppVersion=1.0.0
AppPublisher=thirawat27
AppCopyright=Copyright © 2025, thirawat27
AppPublisherURL=https://github.com/thirawat27
AppSupportURL=https://github.com/thirawat27
DefaultDirName={autopf}\DuckDNS-Connector
DisableProgramGroupPage=yes
OutputDir=.\Installer
OutputBaseFilename=DuckDNS-Connector-v1.0.0-Setup
SetupIconFile=logo.ico
UninstallDisplayIcon={app}\DuckDNS-Connector.exe
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

; --- The [CustomMessages] section is no longer needed and has been removed. ---

[Tasks]
; --- Use plain text directly in the Description and GroupDescription ---
Name: "startupicon"; Description: "Run DuckDNS Connector when Windows starts"; GroupDescription: "Additional icons:"; Flags: unchecked

[Files]
Source: "dist\DuckDNS-Connector.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\DuckDNS Connector"; Filename: "{app}\DuckDNS-Connector.exe"
Name: "{autostartup}\DuckDNS Connector"; Filename: "{app}\DuckDNS-Connector.exe"; Tasks: startupicon

[Run]
Filename: "{app}\DuckDNS-Connector.exe"; Description: "{cm:LaunchProgram,DuckDNS Connector}"; Flags: nowait postinstall shellexec

[UninstallDelete]
Type: files; Name: "{app}\config.ini"
Type: files; Name: "{app}\duckdns_connector.log"