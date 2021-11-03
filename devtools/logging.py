import os, time

class logging:

    def __init__(self, filename):
        self.filename = filename;
        if not os.path.exists(filename):
            open(filename, "w+");
        self.levels = ['INFO', 'WARNING', 'CRITICAL', 'DEBUG'];


    def write(self, msg, level="INFO"):
        if level in self.levels:
            with open(self.filename, 'a') as f:
                f.write("%(asctime)s | %(msg)s | %(level)s\n" % {
                    "asctime" : time.asctime(),
                    "msg" : msg,
                    "level" : level
                })