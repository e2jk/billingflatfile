Virtual environment setup
=========================

Create the environment:
-----------------------
```bash
$ cd devel/billingflatfile/
$ mkdir -p .venv-billingflatfile
$ python3 -m venv .venv-billingflatfile
$ source .venv-billingflatfile/bin/activate
$ pip3 install wheel
$ pip3 install -r requirements.txt
```

Activate the virtual environment:
---------------------------------
`$ source .venv-billingflatfile/bin/activate`

When done:
----------
`$ deactivate`

Update the dependencies:
------------------------
`$ pip3 install -r requirements.txt`

First time creation/update of the dependencies:
-----------------------------------------------
`$ pip3 freeze > requirements.txt`

MS Windows equivalents:
-----------------------
```
mkdir Documents\devel\billingflatfile\.venv-billingflatfile
AppData\Local\Programs\Python\Python38-32\python.exe -m venv Documents\devel\billingflatfile\.venv-billingflatfile
Documents\devel\billingflatfile\.venv-billingflatfile\Scripts\pip3.exe install -r Documents\devel\billingflatfile\requirements.txt
Documents\devel\billingflatfile\.venv-billingflatfile\Scripts\activate.bat
```
