; Instalador de WattBar (Inno Setup). Compilar con ISCC.exe tras generar dist\WattBar con PyInstaller.
#define MyAppName "WattBar"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "nonosky"
#define MyAppURL "https://github.com/nonoskygt/wattbar"
#define MyAppExeName "WattBar.exe"

[Setup]
AppId={{C0FFEE10-7A11-4BAD-9A77-WATTBAR000001}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
DefaultDirName={localappdata}\Programs\WattBar
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
OutputDir=Output
OutputBaseFilename=WattBar-Setup
SetupIconFile=wattbar.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
Compression=lzma2
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "startupicon"; Description: "Iniciar WattBar al encender Windows"; GroupDescription: "Inicio automatico:"

[Files]
Source: "dist\WattBar\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
Name: "{userstartup}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: startupicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Ejecutar WattBar ahora"; Flags: nowait postinstall skipifsilent
