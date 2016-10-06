# Merge panel
Web panel for merge branches and close MR

## Setting up a Merge panel
1. Install virtualenv is a tool to create isolated Python environments
```bash
$ sudo pip install virtualenv
```

2. Creates a virtual environment is the following:
```bash
$ virtualenv flask
```

3. Download modules:
```bash
$ ./flask/bin/pip install -r modules.txt 
```

3. Set variables in [config.py](config.py), for example:
```
GITLAB_SERVER = "http://scm/"
GITLAB_TOKEN = "token"
host = "127.0.0.1"
port = 5002
```

4. Run Merge panel:
```bash
$ ./run.py
```

Or run a command immune to hangups
```bash
$ nohup run.py >> merge_panel.log 2>> merge_panel.log &
```
