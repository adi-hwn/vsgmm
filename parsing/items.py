import json, dota2api

api = dota2api.Initialise(open("../sensitive/steamAPIKey").read().strip())

outputFile = open("./items.json", "w+")

ItemsObj = api.get_game_items()
ItemsDict = {}
for item in ItemsObj["items"]:
    ItemsDict[int(item["id"])] = item

json.dump(ItemsDict, outputFile, indent=2)
