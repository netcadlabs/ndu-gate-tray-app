# NDUGate Service Tray Application

## Features

* [x] Start - Stop service
* [x] Select config file
* [ ] Start at system startup


## Building

```
pyinstaller app.spec
```

* pyinstaller -n "NDUGateApp" --onefile --noconsole app.py

### Resources

* [Packaging PyQt5 & PySide2 applications for Windows, with PyInstaller - by Martin Fitzpatrick](https://www.learnpyqt.com/tutorials/packaging-pyqt5-pyside2-applications-windows-pyinstaller/)