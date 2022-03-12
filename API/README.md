# API

## Installation

### 1. Install Mysql Database

### 2. Synchronize Model with Database

#### Option 1. MySQL Workbench

In MySQLWorkbench go to File -> open Model

Open the Database Model located at "Conlyse/API/Database-Design/V1.mwb" in MySQL Workbench

Go to Database -> Synchronize Model

Enter your MySQL Database credentials and go though the instructions.

### 3. Configure API

Open "constants.py" in a text editor of your choice and enter your MySQL Database connection settings.
FLASK_SECRET is optional to be configured. 
### Done

Now your API should work as intended. Just start it with:

`python3 api.py`