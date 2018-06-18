import dota2api, json, time, sys

#target_id = 20 # Vengeful Spirit
#target_id = 46 # Templar Assassin
#target_id = 9 # Mirana

if len(sys.argv) != 3:
    print(sys.argv[0],"hero_id","data_directory")
    raise ValueError

target_id = int(sys.argv[1])
print(target_id)


target_modes = {
    (22, 7), # AP Ranked
    (3, 7), # RD Ranked
    (2, 7), # CM Ranked
    (22, 0), # AP Unranked
    (16, 0), # Captains Draft
    (5, 0), # All Random
    (4, 0), # Single Draft
    (3, 0),
    (2, 0)
}
outfile_prefix = "sample_match_"
outfile_dir = sys.argv[2]

batch_interval = 4.0
run_interval = 75.0

num_passes_per_batch = 6

api = dota2api.Initialise(open("../sensitive/steamAPIKey").read().strip())
runno = 1

lbFile = open("lbid" + str(target_id) + ".txt", "r")
last_batch_id = int(lbFile.read())
lbFile.close()

total_parsed = 0
passes_left = num_passes_per_batch
recorded_matches = {last_batch_id: True} # Ensure no duplicates
while True:
    batchno = 1

    oldest_match_id = 5000000000
    oldest_match_time = 2000000000
    while oldest_match_id > last_batch_id:
        hdict = api.get_match_history(min_players=10,game_mode=1,hero_id=target_id,start_at_match_id=oldest_match_id)
        print("run",runno,"batch",batchno,"total matches parsed:", total_parsed, "oldest_match_id:", oldest_match_id,hdict["results_remaining"],"/", hdict["total_results"])
        batchno += 1

        if hdict["results_remaining"] == 0:
            break

        for match in hdict["matches"]:
            mid = match["match_id"]
            if match["start_time"] < oldest_match_time:
                oldest_match_time = match["start_time"]
                oldest_match_id=mid
            #print("Testing match", mid)
            if mid in recorded_matches:
                continue
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
                print(match_details["match_id"], (match_details["game_mode"], match_details["lobby_type"]), target_modes)
                if (match_details["game_mode"], match_details["lobby_type"]) in target_modes:
                    total_parsed += 1
                    json.dump(match_details, open(outfile_dir + "/" + outfile_prefix + str(mid), "w+"), indent=0)
                    print("Recorded match", mid)

        time.sleep(batch_interval)

    passes_left -= 1
    if passes_left == 0:
        last_batch_id = max(recorded_matches.keys())
        recorded_matches = {last_batch_id: True}
        passes_left = num_passes_per_batch


    lbFile = open("lbid" + str(target_id) + ".txt", "w")
    lbFile.write(str(max(recorded_matches.keys())))
    lbFile.close()

    print("run",runno,"completed, last_batch_id:", last_batch_id)
    runno += 1
    time.sleep(run_interval)
