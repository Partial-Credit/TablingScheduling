import sys
import csv
import datetime
import copy
import random
import numpy as np
from bs4 import BeautifulSoup 
import urllib.request
import time as time_funct


def delete_escape_chars(string):
    string= string.decode("utf-8")
    string = string.replace("\r", "").replace("\n", "").replace("\t", "")
    string_list = string.split(",")
    return string_list

def whenIsGoodScrapper(whenIsGoodUrl):
    try:
        req = urllib.request.Request(whenIsGoodUrl)
        html  =  urllib.request.urlopen(req).read()
        print("Parsing through WhenIsGood..")
    except Exception as ex:
        print("could not open html file! Not a valid site!")

    try:
        soup = BeautifulSoup(html, 'html.parser')
        data = html.decode("utf-8", errors='replace')
    except Exception as ex:
        print("cant decode char")
    time_slots = soup.find_all('td', ["proposed"])
    people = dict()
    dates = set()
    count = 0
    for time in time_slots:
        slot = dict()
        url = "http://whenisgood.net" + time['onclick'].replace("pop(", "").replace("'", "").replace(",resultspopup);", "")
        req_slot = urllib.request.Request(url)
        html_slot  =  urllib.request.urlopen(req_slot).read()
        soup_slot = BeautifulSoup(html_slot, 'html.parser')
        labels = soup_slot.find_all('tr')
        
        date = (labels[1].find('td', {"class": "field"}).renderContents()).decode('utf-8')
        time = (labels[2].find('td', {"class": "field"}).renderContents()).decode('utf-8')
        can_make_it = delete_escape_chars(labels[3].find('td', {"class": "field"}).renderContents())
        cant_make_it = delete_escape_chars(labels[4].find('td', {"class": "field"}).renderContents())
        
        dates.add(date)
        for person in can_make_it:
            try:
                people[person]
            except:
                people[person] = dict()
            try:
                people[person][time]
            except:
                people[person][time] = dict()  
            people[person][time][date] = "TRUE"
        for person in cant_make_it:
            try:
                people[person]
            except:
                people[person] = dict()
            try:
                people[person][time]
            except:
                people[person][time] = dict()      
            people[person][time][date] = "FALSE"
    
    dates_object = [datetime.datetime.strptime(ts, "%B %d, %Y") for ts in dates]
    dates_object.sort()
    sorteddates = [datetime.datetime.strftime(ts, "%B %d %Y") for ts in dates_object]
    
    with open('input_file.csv', mode = 'w') as table_file:
        table_writer = csv.writer(table_file, delimiter=',', quotechar='"',lineterminator='\n',quoting=csv.QUOTE_MINIMAL)
        for person in people:
            table_writer.writerow([person] + sorteddates)
            for time in people[person]:
                temp = []
                for date in people[person][time]:
                    temp.append(people[person][time][date])
                table_writer.writerow([time] + temp)
    return


def make_dict(schedule, members, predict = None):
    if not predict is None:
        D = copy.deepcopy(predict)
    else:
        D = {}

        for m in members:
            D[m] = 0

    for i in schedule:
        if type(i) is str:
            D[i] += 1

    return D
    

# equality metric, lower is better
def equality(schedule, members, predict = None, itr = 1):
    D = make_dict(schedule, members, predict)
    
    best_avg = float(len(schedule)) / len(members) * itr
    ret = 0

    for i in D.values():
        ret += (i - best_avg) ** 2

    return ret

def schedule(days, slots_per_day, members, member_availability, predict = None, itr = 1):
    N = 300
    
    possible_solutions = [[False] * round(days * slots_per_day)]

    for t in range(round(slots_per_day * days)):
        eq = equality(possible_solutions[0], members, predict, itr)
        new_solutions = []
        choose = list(range(len(members)))
        while len(choose) > 0:
            R = random.randint(0, len(choose) - 1)
            m = choose[R]
            del choose[R]
            if member_availability[m][t]:
                for S in possible_solutions:
                    s = copy.deepcopy(S)
                    s[t] = members[m]
                    new_solutions.append(s)

        if len(new_solutions) > 0:
            next_sols = [new_solutions[0]]
            best = equality(new_solutions[0], members, predict, itr)
            for S in new_solutions[1:]:
                E = equality(S, members, predict, itr)
                if best > E:
                    best = E
                    next_sols = [S]
                elif best == E:
                    next_sols.append(S)
            if len(next_sols) > N:
                possible_solutions = random.sample(next_sols, N)
            else:
                possible_solutions = next_sols
                
    return possible_solutions

if __name__ == "__main__":
    filename = "input_file.csv"
    url = sys.argv[1]
    at_table = int(sys.argv[2])
    times = int(sys.argv[3])
    members = []
    times_available = []
    day_values = []
    start = None
    
    whenIsGoodScrapper(url)

    with open(filename) as f:
        reader = csv.reader(f, delimiter=',', quotechar='|', lineterminator='\n', quoting=csv.QUOTE_MINIMAL)
        days = 0
        slots_per_day = 0
        for row in reader:
            try:
                T = datetime.datetime.strptime(row[0], "%I:%M:%S %p")
                if start is None:
                    start = T
                    
                for i in range(1, len(row)):
                    times_available[-1][i - 1].append(row[i] == "TRUE")

                if len(times_available) == 1:
                    slots_per_day += 1
                    
            except ValueError:
                if len(times_available) > 0:
                    times_available[-1] = [item for sublist in times_available[-1] for item in sublist]

                if days == 0:
                    days = len(row) - 1
                    day_values = row[1:]
                    slots_per_day = 0
                members.append(row[0])
                new_times = []
                for i in range(days):
                    new_times.append([])
                times_available.append(new_times)

        times_available[-1] = [item for sublist in times_available[-1] for item in sublist]

    # convert half hours to longer times...
    slots_per_day /= times
    hour_times = []
    for T in times_available:
        hour_times.append([])
        t = 0
        while t < len(T):
            b = True
            for i in range(times):
                if t + i < len(T) and not T[t + i]:
                    b = False
                    break
                
            hour_times[-1].append(b)
            
            t += times
            
    print("Making tabling schedule for the following members:")
    print(members)
    print("")
    S = []
    D = None
    for i in range(at_table):
        S.append(schedule(days, slots_per_day, members, hour_times, D, i + 1)[0])

        D = make_dict(S[-1], members, D)
        for t, m1 in enumerate(S[-1]):
            for idx, m in enumerate(members):
                if m1 == m:
                    hour_times[idx][t] = False

    with open('result.csv', 'w') as f:
        C = csv.writer(f)
        full_schedule = np.column_stack(S)
        C.writerow([''] + day_values)
        for t in range(int(slots_per_day)):
            row = []
            curr_time = start + datetime.timedelta(minutes=30) * times * (t % slots_per_day)
            row.append(curr_time.strftime("%H:%M"))
            for d in range(days):
                string = ""
                for s in full_schedule[d * int(slots_per_day) + t]:
                    string += s + " "
                row.append(string)
            print(row)
            C.writerow(row)
        
    print(D)
