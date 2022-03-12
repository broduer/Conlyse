# Conlyse
![Dashboard](https://user-images.githubusercontent.com/67592327/158029755-7a860bdb-1d46-4385-a958-a0d8ebdaa061.png)

Conlyse is a project which is all about analysing the browser game "[Conflict of Nations](https://conflictnations.com "Conflict of Nations")".
The project is currently in a state of [PoC](https://en.wikipedia.org/wiki/Proof_of_concept "PoC") because it contains many bugs and has a great potential to improve. I am making that project public because it is growing over my head and I think it is a good idea to show how much potential "Conflict of Nations" has.

## Features
- Every day new reports on economy
- Determines minimum research of enemy countries 
- Lists most valuable cities of enemy countries
- Beautiful graphs of victory points and economy developments 

## Concept
Conlyse contains of four components, each of them is necessary. 
- ###  API
The API connects to the database, reformat the gathered data and sends it to the client. The API is written in python using [flask](https://pypi.org/project/Flask/ "flask"). If you want to use the project in a production environment, which I wouldn't recommend, make sure to disable debug mode for flask.
- ### Bot
The bot is a advanced web scraper which is build in python using selenium and the Python default request package.  It pre sorts the data and writes it to the database. The bot uses cron jobs to run frequently.
- ### Bot Manager
The Bot Manager as the name indicates it manages all the running bots which are tracking different games. Every bot hast to modes normal mode and fast mode. The normal mode should run every 6h if its a 4x speed game and every 24h if it's a 1x speed game because it saves a big amount of data. The normal mode can be run much more frequently because it only saves new newspaper article. Its a work around but in the future I want to add the ability to track own and enemy units and this scan should be run every 5 to 15 min otherwise you could miss important events.
- ### Clients
Currently, only the website is available but other clients might be added later.
#### Website
The website is written in Javascript using react to present the data in a interactive and beautiful way.
## Installation
### Requirements:
- Time
- Patience
- Knowledge about Mysql and Python

First copy the GitHub repository in your desired folder:

`git clone https://github.com/zDox/Conlyse`

Then install all python requirements:
`pip3 -r requirements.txt`

Then first go through the installation of the api then install the Bot and so on.
### [API](https://github.com/zDox/Conlyse/tree/master/API#readme)
### [Bot](https://github.com/zDox/Conlyse/tree/master/Bot_v2#readme)
### [Bot Manager](https://github.com/zDox/Conlyse/tree/master/Bot_Manager#readme)
### [Clients](https://github.com/zDox/Conlyse/tree/master/Clients#readme)
> #### [Website](https://github.com/zDox/Conlyse/tree/master/Clients#Website)
