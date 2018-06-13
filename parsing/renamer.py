import json

rawNamesObj = json.load(open("./hero_names.json"))
trueNamesObj = {"heroes":[]}
outputFile = open("./heroes.json", "w+")

for hero in rawNamesObj["result"]["heroes"]:
    print("Current hero id:", hero["id"], " name:", hero["name"])
    guess_name = hero["name"].replace("npc_dota_hero_","").replace("_"," ").title()
    isTrueName = input("Is this hero called %(guess)s? (y/n)" % {"guess": guess_name})
    if isTrueName == "y":
        heroObj = {"id": hero["id"], "name": hero["name"], "name_en": guess_name}
        trueNamesObj["heroes"].append(heroObj)
    elif isTrueName == "b":
        break
    else:
        input_name = input("Please input name of hero\n")
        heroObj = {"id": hero["id"], "name": hero["name"], "name_en": input_name}
        trueNamesObj["heroes"].append(heroObj)
    print("\n")

json.dump(trueNamesObj, outputFile)
