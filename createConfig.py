import configparser

config = configparser.ConfigParser()

config["Default"] = {
    "host":"localhost",
    "database":"/db/tpvapp.db"
}

with open("config.ini", "w") as cofigfile:
    config.write(cofigfile)