import json
import datetime
from pathlib import Path

file_to_save = 'LastExecutionCandidatesData.json'

def myconverter(o):
    if isinstance(o, datetime.datetime):
        return "{}-{}-{}".format(o.year, o.month, o.day)

def get_last_saved_stats_for_candidates():
    my_file = Path(file_to_save)
    if my_file.is_file():
        with open(file_to_save, "r") as read_file:
            data = json.load(read_file)
    else:
        data={}
    return data


def update_last_saved_stats_for_candidates(candidatesLive):
    with open(file_to_save, "w") as write_file:
        json.dump(candidatesLive, write_file, default = myconverter)
    pass
