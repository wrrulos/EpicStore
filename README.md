# EpicStore
<h3> Discord bot to keep up with free games from Epic Games </h3>
<br/>
<p align='center'> <img src='https://imgur.com/Qn18Yyf.jpg' title='EpicStore-Title'> </p>
<br/>

# 🔧 Installation 

```bash
# Install Python 3 (https://www.python.org/)

# Clone the repository (Or download it from the web in the "Code button and download zip")
$ git clone https://github.com/wrrulos/MCPTool

# Go into the MCPTool folder
$ cd MCPTool

# Install dependencies 
$ python3 -m pip install -r requirements.txt
```

# Usage

<h3> First you must enter the token in the configuration file (settings.json).

Then just put python3 main.py in the terminal</h3>

# How does it work?

<p> First of all, it should be mentioned that every hour the bot sends a request to the Epic Games API to obtain the games that are free at that moment. Also, save the name of the games in the 'games' section of the data file of all servers. (The latter is done if the current value is different from the previous one)</p>

<img src='https://imgur.com/RTeDXc0.jpg' title='games'>

<p> If the current value (name of the games) is different from the previous one, it sends an announcement to the channel specified by the user. </p>

<img src='https://imgur.com/PRTfCjM.jpg' title='message'>
