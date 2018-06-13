import dota2api, json, time

target_id = 20 # Vengeful Spirit
target_mode = 22 # AP
target_lobby = 7 # Ranked
outfile_prefix = "sample_match_"

batch_interval = 8.0
run_interval = 120.0

num_passes_per_batch = 2

api = dota2api.Initialise(open("../sensitive/steamAPIKey").read().strip())
runno = 1

last_batch_id = 3950056442
total_parsed = 0
passes_left = num_passes_per_batch
recorded_matches = {last_batch_id: True} # Ensure no duplicates
while True:
    batchno = 1

    oldest_match_id = 5000000000
    oldest_match_time = 2000000000
    while oldest_match_id > last_batch_id:
        print("run",runno,"batch",batchno,"total matches parsed:", total_parsed, "oldest_match_id:", oldest_match_id)
        batchno += 1
        hdict = api.get_match_history(hero_id=target_id,game_mode=target_mode,start_at_match_id=oldest_match_id)

        for match in hdict["matches"]:
            mid = match["match_id"]
            if mid < oldest_match_id:
                oldest_match_id=mid
            #print("Testing match", mid)
            if mid in recorded_matches:
                continue
            if match["lobby_type"] == target_lobby:
                has_leaver = False
                found_target = False
                match_details = api.get_match_details(match_id=mid)
                #print("Fetched match", mid)
                recorded_matches[mid] = True
                for player in match_details["players"]:
                    if player["leaver_status"] != 0:
                        has_leaver = True
                    if player["hero_id"] == target_id:
                        found_target = True
                if found_target and not has_leaver:
                    total_parsed += 1
                    json.dump(match_details, open("json/" + outfile_prefix + str(mid), "w+"), indent=0)
                    print("Recorded match", mid)

        time.sleep(batch_interval)

    passes_left -= 1
    if passes_left == 0:
        last_batch_id = max(recorded_matches.keys())
        recorded_matches = {last_batch_id: True}
        passes_left = num_passes_per_batch

    print("run",runno,"completed, last_batch_id:", last_batch_id)
    runno += 1
    time.sleep(run_interval)
