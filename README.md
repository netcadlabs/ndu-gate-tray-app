# NDUGate Service Tray Application

## Features

* [x] Start - Stop the ndu-gate service
* [ ] Start - Stop the thingsboard gateway service
* [x] Select and set config files
* [ ] Start at system startup
* [ ] Prevent multiple instances of the app running
* [ ] Logging


## Building

```
pyinstaller --nowindow .\app.spec
```

--- 
### Resources

* [Packaging PyQt5 & PySide2 applications for Windows, with PyInstaller - by Martin Fitzpatrick](https://www.learnpyqt.com/tutorials/packaging-pyqt5-pyside2-applications-windows-pyinstaller/)
* [InstallForge to prepare windows installation](https://installforge.net/)
* [Manage the Programs Run at Windows Startup](https://www.akadia.com/services/windows_registry.html)
* [tendo - prevent multiple instance of app running](https://github.com/pycontribs/tendo)