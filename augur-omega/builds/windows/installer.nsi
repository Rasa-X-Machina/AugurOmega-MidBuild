; NSIS script for Augur Omega Windows Installer
!define APP_NAME "Augur Omega"
!define APP_VERSION "1.0.0"
!define APP_PUBLISHER "Augur Omega AI"
!define APP_URL "https://augur-omega.ai"

Outfile "AugurOmega-Setup-${APP_VERSION}.exe"
InstallDir $PROGRAMFILES64\AugurOmega

Section "Augur Omega" SecMain
  SetOutPath $INSTDIR
  File "augur_omega.exe.py"
  CreateShortCut "$SMPROGRAMS\$APP_NAME.lnk" "$INSTDIR\augur_omega.exe.py"
SectionEnd
