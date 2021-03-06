from html.parser import HTMLParser
import urllib3

class RadioProgram():
    
    def __init__(self, start, stop, name):
        self.start = start
        self.stop = stop
        self.name = name

# create a subclass and override the handler methods
class MyHTMLParser(HTMLParser):

    def __init__(self):
        #super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs= True
        self.fed = []
        self.breadcrumps = []
        self.programs = []
        self.current_prog_start_utc = ""
        self.current_prog_start_cat = ""
        self.current_prog_name  = ""
        self.record = False

    def handle_starttag(self, tag, attrs):
        #print("Encountered a start tag:", tag)
        self.breadcrumps.append(tag)
        marker = ['html', 'head', 'meta', 'body', 'div', 'div', 'div', 'div', 'section', 'div', 'ul', 'form', 'div', 'div', 'div', 'h5']
        if self.breadcrumps == marker:
            self.record = True
        
    def handle_endtag(self, tag):
        #print("Encountered an end tag :", tag)
        self.breadcrumps.pop()
        
    def handle_data(self, data):
        if self.record:
            if self.current_prog_start_utc == "":
                self.current_prog_start_utc = data
                # ignore UTC
                pass
            elif self.current_prog_start_cat == "":
                self.current_prog_start_cat = data
                # CAT - Centrle Africa Time
                if len(self.programs) > 0:
                    # get last recognized program and input stop-time
                    lastProg = self.programs[len(self.programs)-1]
                    lastProg.stop = self.current_prog_start_cat
                    
            elif self.current_prog_name == "":
                self.current_prog_name = data
                # default will be overwirten, when I know that the next
                # program is starting
                # for the last program on that day it is also correct like that
                default_end_time = '24:00'
                
                p = RadioProgram(self.current_prog_start_cat, 
                                default_end_time,
                                self.current_prog_name)
                self.programs.append(p)
                self.current_prog_start_utc = ""
                self.current_prog_start_cat = ""
                self.current_prog_name  = ""
        self.record = False 
        #print("bread-crumps: ", self.breadcrumps)
        #print("Encountered some data  :", data)

    def get_data(self):
        print(self.fed)
        return ''.join(self.fed)

    def getPrograms(self):
        return self.programs


class Schedule:
    
    class Row:
        
        def __init__(self, time_formated, time_mins):
            self.time_formated = time_formated
            self.time_mins = time_mins
            self.col = []
            self.col.append("") # monday
            self.col.append("") # tuesday
            self.col.append("") # wednesday
            self.col.append("") # thursday
            self.col.append("") # friday
            self.col.append("") # saturday
            self.col.append("") # sunday
            
        def setProgram(self, col, program_name):
            self.col[col] = program_name

    def __init__(self, convert_comma_to_semicolon=False):
        self.convert_comma_to_semicolon = convert_comma_to_semicolon
        self.rows = []
        
        for minute in range(24*60):            
            time_mins = minute
            time_formanted = '%02d:%02d' % (minute/60, minute%60)
            row = Schedule.Row(time_formanted, time_mins)
            self.rows.append(row)
        
    
    
    def getRows(self):
        return self.rows
    
    def addProgram(self, day, start_formated, end_formated, name):
        hour= int(start_formated.split(":")[0])
        minute = int(start_formated.split(":")[1])
        
        start_mins = hour*60+minute
        
        hour= int(end_formated.split(":")[0])
        minute = int(end_formated.split(":")[1])
        end_mins = hour*60+minute
        
        for i in range(start_mins, end_mins):
            if self.convert_comma_to_semicolon:
                name = name.replace(",", ";")
            self.rows[i].col[day] = name

class Formater():
    
    def __init__(self, seperator="-", space_for_entries=40, show_header=False):
        self.seperator = seperator
        self.space_for_entries = space_for_entries
        self.show_header = show_header
    
    def format(self, obj_to_format):
        output = ""
        if self.show_header:
            for header in ["Time", "Monday", "Tuesday", "Wednesday", "Thursday", "Fireday", "Saturday", "Sunday"]:
                output += header + self.seperator
            output += "\n"
        for row in range(0, len(obj_to_format.getRows())):
            output += obj_to_format.getRows()[row].time_formated + self.seperator
            for col in range(0, len(obj_to_format.getRows()[row].col)):
                
                output +=  " {0:^{2}} {1} ".format(obj_to_format.getRows()[row].col[col], self.seperator, 40)
            output += "\n"
        return output;

class Downloader:
    
    def __init__(self):
        self.mon = ["monday", "https://www.twrafrica.org/index.php/component/schedules/?task=days.weekdays&dow=1&tx=4"]
        self.tue = ["tuesday", "https://www.twrafrica.org/index.php/component/schedules/?task=days.weekdays&dow=2&tx=4"]
        self.wed = ["wednesday", "https://www.twrafrica.org/index.php/component/schedules/?task=days.weekdays&dow=3&tx=4"]
        self.thu = ["thursday", "https://www.twrafrica.org/index.php/component/schedules/?task=days.weekdays&dow=4&tx=4"]
        self.fri = ["friday", "https://www.twrafrica.org/index.php/component/schedules/?task=days.weekdays&dow=5&tx=4"]
        self.sat = ["saturday", "https://www.twrafrica.org/index.php/component/schedules/?task=days.weekdays&dow=6&tx=4"]
        self.sun = ["sunday", "https://www.twrafrica.org/index.php/component/schedules/?task=days.weekdays&dow=7&tx=4"]
        self.week = [self.mon, self.tue, self.wed, self.thu, self.fri, self.sat, self.sun]
        
    def file_name(self, day, folder):
        return folder + "/" + day[0] + ".html"
    
    def download(self, folder):
        progs = []
        
        http = urllib3.PoolManager()
        
        for day in self.week:
            print("download " + day[0])
            
            response = http.request('GET', day[1], preload_content=False)
            print("response: " + str(response.status))
            f = open(self.file_name(day,folder ), 'w')
            f.write(response.data.decode("utf-8"))
            f.close

    def get_offline(self, folder):
        progs = []
        
        for day in self.week:
            txt = open(self.file_name(day, folder))
            wholeFile = txt.read() # read whole file at once
            txt.close()
            
            parser = MyHTMLParser()
            parser.feed(wholeFile)
            progs.append(parser.getPrograms())
        return progs

if __name__ == '__main__':
    worker = Downloader()
    progsPerDay = worker.download("tmp")
    progsPerDay = worker.get_offline("tmp")
    schedule = Schedule()
    
    for day in range(0, len(progsPerDay)):
        #print("***********************day: ", day)
        for prog in range(0, len(progsPerDay[day])):
            progData = progsPerDay[day][prog]
            #print("progData: %s, %s, %s" % (progData.start, progData.stop, progData.name))
            schedule.addProgram(day, progData.start, progData.stop, progData.name)
    
    formater = Formater(seperator=",", show_header=True)
    
    output = formater.format(schedule)
    
    file = open("schedule.csv", 'w')
    file.truncate()     # delete content of file
    file.write(output)  # write text to file
    file.close()
    print("finished")