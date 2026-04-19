# Commands to run for development

This is a list of commands helpful for the development and run the application

## Backend Commands

Commands to develop/run the application backend. This is the BRAIN (back bone) of the project.

### Create backend directory

```
mkdir backend
```

### Open backend directory

```
cd backend
```

### Create Virtual Environment

```
py -m venv .venv
```

### Activate the Virtual Environment

```
.venv\Scripts\activate
```


### Update PIP
```
python.exe -m pip install --upgrade pip
```

### Install Dependencies

```
pip install -r requirements.txt
```

### Install Python 3.11 to resolve wheel issue

**If Python 3.11 is not available in the system then run:**

```
winget search Python.Python.3.11

winget install Python.Python.3.11
```

**Install Virtual Environment with Python 3.11 version**

```
py -3.11 -m venv .venv
```

**Activate Virtual Environment**

```
.venv\Scripts\activate
```

### Install Dependencies

```
pip install -r requirements.txt
```