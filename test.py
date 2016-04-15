import unittest
from download_url import MyHTMLParser, Schedule, Formater, Downloader

class TestDownloader(unittest.TestCase):
    
    def test_get_offline(self):
        cut = Downloader()
        allProgs = cut.get_offline("test")
        
        self.assertEqual(len(allProgs), 7)
        
        # Monday
        self.assertEqual(len(allProgs[0]), 63)
        self.assertEqual(allProgs[0][62].name, "Dorothy's Daily Devotionals")
        
        # Tuesday
        self.assertEqual(len(allProgs[1]), 64)
        self.assertEqual(allProgs[1][63].name, "Dorothy's Daily Devotionals")
        
        # Wednesday
        self.assertEqual(len(allProgs[2]), 63)
        self.assertEqual(allProgs[2][62].name, "Dorothy's Daily Devotionals")
        
        # Thursday
        self.assertEqual(len(allProgs[3]), 63)
        self.assertEqual(allProgs[3][62].name, "Dorothy's Daily Devotionals")
        
        # Firday
        self.assertEqual(len(allProgs[4]), 63)
        self.assertEqual(allProgs[4][62].name, "Dorothy's Daily Devotionals")
        
        # Saturday
        self.assertEqual(len(allProgs[5]), 45)
        self.assertEqual(allProgs[5][44].name, "Music Till Midnight")
        
        # Sunday
        self.assertEqual(len(allProgs[6]), 52)
        self.assertEqual(allProgs[6][51].name, "Music Till Midnight")
        

class TestHTMLParser(unittest.TestCase):
    
    DATA = "test/monday.html"
    
    def test_learning(self):
        listOne = ["one", "two"]
        listTwo = ["one", 'two']
        
        self.assertTrue(listOne == listTwo)
    
    def test_parse_monday(self):
        cut = MyHTMLParser()
        txt = open(TestHTMLParser.DATA)
        wholeFile = txt.read() # read whole file at once
        txt.close()
        cut.feed(wholeFile)
        progs = cut.getPrograms()
        self.assertEqual(len(progs), 63)
        self.assertEqual(progs[0].start, "00:00:00")
        self.assertEqual(progs[0].stop , "00:15:00")
        self.assertEqual(progs[0].name , "Radio Bible")
        
        self.assertEqual(progs[1].start, "00:15:00")
        self.assertEqual(progs[1].stop , "00:45:00")
        self.assertEqual(progs[1].name , "Back to the Bible")
        
        self.assertEqual(progs[62].start, "23:45:00")
        self.assertEqual(progs[62].stop , "24:00")
        self.assertEqual(progs[62].name , "Dorothy's Daily Devotionals")

class TestFormater(unittest.TestCase):
    
    def test_format_one_day(self):
        cut = Formater()
        schedule = Schedule()
        schedule.addProgram(0, "00:00", "00:02", "test on 1")
        schedule.addProgram(0, "23:00", "24:00", "late test on 1")
        result = cut.format(schedule)
        lines = result.split(sep="\n")
        self.assertRegexpMatches(lines   [0], "00:00-(\ *)test on 1(\ *)-(\ *)-(\ *)-(\ *)-(\ *)-(\ *)-(\ *)-")
        self.assertRegexpMatches(lines   [1], "00:01-(\ *)test on 1(\ *)-(\ *)-(\ *)-(\ *)-(\ *)-(\ *)-(\ *)-")
        self.assertRegexpMatches(lines   [2], "00:02-(\ *)-(\ *)-(\ *)-(\ *)-(\ *)-(\ *)-(\ *)-")
        self.assertRegexpMatches(lines[1438], "23:58-(\ *)late test on 1(\ *)-(\ *)-(\ *)-(\ *)-(\ *)-(\ *)-(\ *)-")
        self.assertRegexpMatches(lines[1439], "23:59-(\ *)late test on 1(\ *)-(\ *)-(\ *)-(\ *)-(\ *)-(\ *)-(\ *)-")


    def test_format_two_days(self):
        cut = Formater()
        schedule = Schedule()
        schedule.addProgram(0, "00:00", "00:02", "test on 1")
        schedule.addProgram(1, "00:00", "24:00", "test on 2")
        schedule.addProgram(0, "23:00", "24:00", "late test on 1")
        result = cut.format(schedule)
        lines = result.split(sep="\n")
        self.assertRegexpMatches(lines   [0], ".*")
        self.assertRegexpMatches(lines   [0], "00:00-(\ *)test on 1(\ *)-(\ *)test on 2(\ *)-(\ *)-(\ *)-(\ *)-(\ *)-(\ *)-")
        self.assertRegexpMatches(lines   [1], "00:01-(\ *)test on 1(\ *)-(\ *)test on 2(\ *)-(\ *)-(\ *)-(\ *)-(\ *)-(\ *)-")
        self.assertRegexpMatches(lines   [2], "00:02-              (\ *)-(\ *)test on 2(\ *)-(\ *)-(\ *)-(\ *)-(\ *)-(\ *)-")
        self.assertRegexpMatches(lines[1438], "23:58-(\ *)late test on 1(\ *)-(\ *)test on 2(\ *)-(\ *)-(\ *)-(\ *)-(\ *)-(\ *)-")
        self.assertRegexpMatches(lines[1439], "23:59-(\ *)late test on 1(\ *)-(\ *)test on 2(\ *)-(\ *)-(\ *)-(\ *)-(\ *)-(\ *)-")


class TestSchedule(unittest.TestCase):
    
    def test_rows(self):
        cut = Schedule()
        self.assertTrue(len(cut.getRows()), 24*60)
        self.assertEqual(cut.getRows()[0].time_mins, 0)
        self.assertEqual(cut.getRows()[0].time_formated, "00:00")
        
        self.assertEqual(cut.getRows()[1].time_mins, 1)
        self.assertEqual(cut.getRows()[1].time_formated, "00:01")
        
        self.assertEqual(cut.getRows()[61].time_mins, 61)
        self.assertEqual(cut.getRows()[61].time_formated, "01:01")
        
        self.assertEqual(cut.getRows()[1439].time_mins, 1439)
        self.assertEqual(cut.getRows()[1439].time_formated, "23:59")
    
    def test_schedule_simple(self):
        cut = Schedule()
        cut.addProgram(1, "00:00", "00:01", "test 123")
        self.assertEqual(cut.getRows()[0].col[1], "test 123")
        self.assertEqual(cut.getRows()[1].col[1], "")
        self.assertEqual(cut.getRows()[2].col[1], "")
    
    def test_schedule_more(self):
        cut = Schedule()
        cut.addProgram(1, "00:00", "00:01", "test 1")
        cut.addProgram(2, "00:00", "00:03", "test 2")
        self.assertEqual(cut.getRows()[0].col[1], "test 1")
        self.assertEqual(cut.getRows()[0].col[2], "test 2")
        self.assertEqual(cut.getRows()[1].col[1], "")
        self.assertEqual(cut.getRows()[1].col[2], "test 2")
        self.assertEqual(cut.getRows()[2].col[1], "")
        self.assertEqual(cut.getRows()[2].col[2], "test 2")
        self.assertEqual(cut.getRows()[3].col[1], "")
        self.assertEqual(cut.getRows()[3].col[2], "")
    
    def test_schedule_more_at_end(self):
        cut = Schedule()
        cut.addProgram(0, "00:00", "00:02", "test on 1")
        cut.addProgram(0, "23:00", "24:00", "late test on 1")
        self.assertEqual(cut.getRows()[1439].col[0], "late test on 1")

if __name__ == '__main__':
    unittest.main()    