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

batch_interval = 3.0
run_interval = 75.0

num_passes_per_batch = 6

api = dota2api.Initialise(open("../sensitive/steamAPIKey").read().strip())
runno = 1

lbFile = open("lbid" + str(target_id) + ".txt", "r")
last_batch_id = int(lbFile.read())
lbFile.close()

total_parsed = 0
passes_left = num_passes_per_batch
while True:
    print("total parsed so far:", total_parsed)
    mlist = api.get_match_history_by_seq_num(matches_requested=100,start_at_match_seq_num=last_batch_id+1)
    for match in mlist["matches"]:
        last_batch_id = max(last_batch_id, match["match_seq_num"])
        if match["human_players"] == 10:
            mid = match["match_id"]
            has_leaver = False
            found_target = False
            #print("Fetched match", mid)
            for player in match["players"]:
                if player["leaver_status"] != 0:
                    has_leaver = True
                if player["hero_id"] == target_id:
                    found_target = True
            if found_target and not has_leaver:
                #print(match["match_id"], (match["game_mode"], match["lobby_type"]), target_modes)
                if (match["game_mode"], match["lobby_type"]) in target_modes:
                    total_parsed += 1
                    json.dump(match, open(outfile_dir + "/" + outfile_prefix + str(mid), "w+"), indent=0)
                    print("Recorded match", mid)


    lbFile = open("lbid" + str(target_id) + ".txt", "w")
    lbFile.write(str(last_batch_id))
    lbFile.close()

    time.sleep(batch_interval)