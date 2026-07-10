[Setup]
AppId={{B3E2C1A4-6F1D-4C7A-9E2B-2F6B7C9A1D3E}}
AppName=yt-dlp GUI
AppVersion=1.0.0
AppPublisher=Harll3kin
DefaultDirName={autopf}\yt-dlp GUI
DefaultGroupName=yt-dlp GUI
DisableProgramGroupPage=yes
OutputDir=output
OutputBaseFilename=ytdlp-gui-setup
Compression=lzma2
SolidCompression=yes
ArchitecturesInstallIn64BitMode=x64compatible
UninstallDisplayIcon={app}\ytdlp-gui.exe

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional shortcuts:"

[Files]
Source: "..\dist\ytdlp-gui.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\bin\yt-dlp.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\bin\ffmpeg.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\yt-dlp GUI"; Filename: "{app}\ytdlp-gui.exe"
Name: "{group}\Uninstall yt-dlp GUI"; Filename: "{uninstallexe}"
Name: "{autodesktop}\yt-dlp GUI"; Filename: "{app}\ytdlp-gui.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\ytdlp-gui.exe"; Description: "Launch yt-dlp GUI"; Flags: nowait postinstall skipifsilent
