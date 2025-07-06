import json
import re
from save import save_to_json
from needleman_wunsch import needleman_wunsch
from compare_aligned_lines import compare_aligned_lines_intervals, compare_aligned_lines, trim_sequences
import time
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


results = {}
checked_pairs = set()

# Open and load JSON file
with open("files/medmel_corpus.json", "r", encoding="utf-8") as file:
    medmel_data = json.load(file)

# Open and load JSON file
with open("files/known_connections.json", "r", encoding="utf-8") as file:
    known_connections = json.load(file)


def recover_results():
    global results
    with open("files/results/pitch/spaces-true/results.json", "r", encoding="utf-8") as file:
        results = json.load(file)


def compare_corpus(medmel_data, params, song_n=0):
    global results
    tot_n = len(medmel_data)
    print("Starting")
    if song_n > 0:
        results = recover_results()
    while song_n < tot_n:
        start_time = time.time()

        song = medmel_data[song_n]
        compare_song(song, medmel_data, params)
        save_to_json(results, filename="files/results/pitch/spaces-true/results.json")

        elapsed = time.time() - start_time
        logging.info(f"Finished song {song["id"]} in {elapsed:.2f} seconds ({song_n}/{tot_n} | {round(song_n * 100 / tot_n, 2)}%)")
        song_n += 1

def compare_song(song_source, medmel_data, params):
    global results
    global checked_pairs
    melody = select_pitch_or_interval(song_source, params)

    # Loop through lines of source melody
    for l_n_source, source_line in enumerate(melody):
        if len(source_line) > 2:
            source_line = apply_params(source_line, params)

            # loop through database (target melodies)
            for target_song in medmel_data:
                # Do not compare a song with itself or other manifestations of self in other source
                # (song_source["id"] is the repertory number)
                pair = tuple(sorted((song_source["id_staves"], target_song["id_staves"])))

                if target_song["id"] == song_source["id"] or pair in checked_pairs:
                    continue
                if song_source["id"] in known_connections and \
                        target_song["id"] in known_connections[song_source["id"]]:
                    print("skipping " + target_song["id"] + " and " + song_source["id"])
                    continue

                # select melody (pitch or transposed)
                target_melody = select_pitch_or_interval(target_song, params)

                # Loop through target melody
                for l_n_target, target_line in enumerate(target_melody):
                    if len(target_line) <= 2:
                        continue

                    if params["transpose"]:
                        source_line_directionless = re.sub(r'[+\-=]', '', source_line)
                        source_line_direction = re.sub(r'[^+\-=]', '', source_line)

                        # Remove direction markers from the compare sequence
                        target_line_directionless = re.sub(r'[+\-=]', '', target_line)
                        target_line_direction = re.sub(r'[^+\-=]', '', target_line)

                        # Perform Needleman-Wunsch on directionless intervals
                        source_line_nw, target_line_nw = needleman_wunsch(source_line_directionless,
                                                                          target_line_directionless)
                        # Trim results if required
                        if not params["exact_search"]:
                            source_line_nw, target_line_nw = trim_sequences(source_line_nw, target_line_nw)

                        similarity, matches = compare_aligned_lines_intervals(source_line_nw,
                                                                              target_line_nw,
                                                                              source_line_direction,
                                                                              target_line_direction)
                    else:
                        # Perform Needleman-Wunsch on pitch
                        source_line_nw, target_line_nw = needleman_wunsch(source_line, target_line)

                        # Trim results if required
                        if not params["exact_search"]:
                            source_line_nw_trimmed, target_line_nw_trimmed = trim_sequences(source_line_nw, target_line_nw)
                            similarity, matches = compare_aligned_lines(source_line_nw_trimmed, target_line_nw_trimmed)
                        else:
                            similarity, matches = compare_aligned_lines(source_line_nw, target_line_nw)

                    # Convert to percentage and round
                    score = round(min(similarity * 100, 100), 2)
                    if score > params["tolerance"]:
                        result = {
                            "score": score,
                            "matches": matches,
                            "source": {
                                "id": song_source["id_staves"],
                                "n": l_n_source,
                                "ms": song_source["ms"],
                                "f": song_source["f"],
                                "melody_line": song_source["staves"][l_n_source],
                                "text": song_source["text"][l_n_source] if l_n_source < len(song_source["text"]) else ""

                            },
                            "target": {
                                "id": target_song["id_staves"],
                                "n": l_n_target,
                                "ms": target_song["ms"],
                                "f": target_song["f"],
                                "melody_line": target_song["staves"][l_n_target],
                                "text": target_song["text"][l_n_target] if l_n_target < len(target_song["text"]) else ""
                            }
                        }
                        if song_source["id_staves"] in results:
                            results[song_source["id_staves"]].append(result)
                        else:
                            results[song_source["id_staves"]] = [result]

            # Remember that this source-target pair has already been checked
            checked_pairs.add(pair)


def apply_params(source_line, params):
    if not params["consider_spaces"]:
        source_line = source_line.replace(" ", "")
    if not params["consider_plica"]:
        source_line = source_line.replace(r"[()]", "")
    return source_line


def select_pitch_or_interval(song, params):
    if params["transpose"]:
        return song["intervals"]
    else:
        return song["staves"]

def restructure_corpus():
    corpus = {}
    for song in medmel_data:
        corpus[song["id_staves"]] = song
    return corpus


def integrate_results(results):
    corpus = restructure_corpus()
    new_results = {}

    for staves_id in results:
        source_info = {k: v for k, v in corpus[staves_id].items() if k != 'intervals'}
        new_results[staves_id] = {"source": source_info, "matches": []}
        matches = results[staves_id]
        for m in matches:
            target = m["target"]
            target_id = target["id"]
            target["id_staves"] = target_id
            target["title"] = corpus[target_id]["title"]
            target["author"] = corpus[target_id]["author"]
            target["id"] = corpus[target_id]["id"]

            match = {
                "score": m["score"],
                "matches": m["matches"],
                "source_line": m["source"]["n"],
                "target": target
            }

            new_results[staves_id]["matches"].append(match)

    return new_results

def get_path(params):
    path = "files/results/"
    if params["transpose"]:
        path += "transpose/"
    else:
        path += "pitch/"

    if params["consider_spaces"]:
        path += "spaces-true/"
    else:
        path += "spaces-false/"

    if params["exact_search"]:
        path += "trim-false/"
    else:
        path += "trim-true/"

    return path + "results.json"

# PARAMETERS
params = {
    "tolerance": 90,
    "consider_spaces": False,
    "transpose": False,
    "exact_search": True,
    "consider_plica": False
}
results_path = get_path(params)
results = {}
startAt = 0
# user_input = input("Do you want to start from the beginning? (y / number) ").strip()
#
# if user_input.lower() == 'y':
#     startAt = 0
# elif user_input.isdigit():  # Checks if input is a number
#     startAt = int(user_input)
# else:
#     print("Aborting...")
#     exit()

START_TIME = time.time()

print(f"Starting at: {startAt}")
compare_corpus(medmel_data, params, startAt)
results = integrate_results(results)
save_to_json(results, filename=results_path)


elapsed = time.time() - START_TIME
print("FINISHED at " + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + " it took " + str(elapsed/60) + " minutes")
print("Saved in " + results_path)