import requests
import ratelimit
import json
import os
import sys
from progress import printProgressBar #From stackoverflow https://stackoverflow.com/questions/3173320/text-progress-bar-in-the-console

non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0xfffd) #stackoverflow

save_directory = "dump"

class Fetcher:
        """
        The Fetcher object is a mildly complex solution to a simple problem: How to download TF2 logs
        There are very minimal filtering options here, as that should be done by the library.
        'sink' is either file or object, which is where to save logs in fetch()
        sinking to a file should be done ahead of time before processing, probably
        sinking to an object will also take a lot of time and should only be done with a limited log range
        param earliest: Earliest log to include (inclusive)
        param latest: Latest log to include (inclusive)
        """
        def __init__(self, sink, ID64, earliest=0, latest=999999999, save_directory=save_directory, skip_init=False):
                self.save_directory = save_directory
                if sink == 'file':
                        self.sink = 'file'
                        if not os.path.isdir(save_directory):
                                os.makedirs(save_directory)
                elif sink == 'object':
                        self.sink = 'object'
                else:
                        raise Exception("Unknown sink: use: `file` or `object`")
                if not skip_init:
                        if not os.path.isdir(save_directory):
                                os.mkdir(save_directory)
                                print("Creating dir {}".format(save_directory))
                        logs = self.get_big_list(ID64)
                        self.all = [l for l in logs if earliest <= l['id'] <= latest and 12 <= l['players'] <= 15]
                else:
                        self.all = []

        def get_big_list(self, me64, limit=10000, offset=0):
                """
                Get all the log ids for the provided ID
                """
                req = "http://logs.tf/api/v1/log?player={}&limit={}&offset={}".format(me64, limit, offset)
                r = requests.get(req)
                return r.json()["logs"]
                
        def fetch(self, do_progress_bar=False, do_file_return=False):
                """
                Get detailed logs
                If your Fetcher object sinks to objects, this returns a massive list of json log objects.
                If your Fetcher object sinks to files, this downloads them.
                * To retrieve downloaded logs, you can manually call Fetcher.from_dir() or
                *  set do_file_return to True in Fetcher.fetch()
                """
                mem = [] #For objects held in memory (i.e. not sinked to file)
                for i, l in enumerate(self.all):
                        id = l['id']
                        fn = "{}{}log_{}.json".format(self.save_directory, os.sep, id)
                        if do_progress_bar:
                                printProgressBar(i+1, len(self.all), prefix="Progress", length=60)
                        if os.path.isfile(fn) and self.sink == "file":
                                continue
                        json_obj = self.get_detailed(id)               
                        if self.sink == "file":
                                with open(fn, "w+", encoding="utf-8") as f:
                                        json.dump(json_obj, f, ensure_ascii=False, indent=4)
                        else:
                                mem.append(json_obj)
                if self.sink == 'object':
                        return mem
                elif do_file_return:
                        return self.from_dir()
                
        def from_dir(self):
                l = []
                for file in os.listdir(self.save_directory):
                        with open(os.path.join(self.save_directory, file), 'r', encoding="utf8") as f:
                                log = json.load(f)
                                log["id"] = file.split("_")[1].split(".")[0]
                                l.append(log)
                return l

        @ratelimit.sleep_and_retry
        @ratelimit.limits(calls=30, period=1)
        def get_detailed(self, id):
                r = requests.get("http://logs.tf/api/v1/log/{}".format(id))
                if r.status_code != 200:
                        print("Unexpected status code {} for log {}".format(r.status_code, id))
                return r.json()
