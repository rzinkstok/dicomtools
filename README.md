DICOM tools
===========

Simple tools to work with DICOM files.

DicomDump
---------

View the content of a DICOM file, search through it and convert to text file. 
Supports dropping a DICOM file onto the application icon.

Create executable
-----------------

Use [`pyinstaller`](https://www.pyinstaller.org) to create an executable:

```
pyinstaller -w -F DicomDump.py
```
The `-w` flag makes sure no console is started, the `-F` flag creates a single file 
executable.