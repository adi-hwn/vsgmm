import dota2api, json

target_id = 20 # Vengeful Spirit

api = dota2api.Initialise(open("../sensitive/steamAPIKey").read().strip())
hdict = api.get_match_history(matches_requested=1000,hero_id=target_id,game_mode=22)

json.dump(hdict, open("./json/history.json","w+"),indent=2)
