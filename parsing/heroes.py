import json, dota2api

api = dota2api.Initialise(open("../sensitive/steamAPIKey").read().strip())

outputFile = open("./heroes.json", "w+")

HeroesObj = api.get_heroes()
HeroesDict = {}
for hero in HeroesObj["heroes"]:
    HeroesDict[int(hero["id"])] = hero

json.dump(HeroesDict, outputFile, indent=2)
