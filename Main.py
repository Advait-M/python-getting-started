from flask import Flask, render_template
import random
import pyredb
import time

app = Flask(__name__)

    
def hexadecimalf():
    hexadecimal = "#"
    sumi = 0
    for i in range(0, 6):
        a = random.randint(48, 70)
        while 58 <= a <= 64:
            a = random.randint(48,70)
        hexadecimal += chr(a)
        sumi += a
    if sumi < 700:
        return hexadecimal
    else:
        return hexadecimalf()

@app.route("/")
def index():
    data = pyredb.WaitNoMore().getAll()
    names = []

    clinicNames= []
    for obj1 in range(len(data)):
        clinicNames.append(data[obj1][4])
    clinicNames = list(set(clinicNames))

    colors = {}
    for i in range(0, len(clinicNames)):
        colors[clinicNames[i]] = hexadecimalf()
    for obj1 in range(len(data)):
        clinicInfo = {
            'clinic_name' : data[obj1][4],
            'end_time' : data[obj1][1],
            'location' : data[obj1][3],
            'start_time': data[obj1][0],
            "color": colors[data[obj1][4]]
        }
        print(clinicInfo["color"])


        names.append(clinicInfo)



    waitTimes = findWaitTime(data, clinicNames)
    times = []
    wait = ""
    temp = ""
    for i in range(len(waitTimes)):
        temp = waitTimes[i][1]
        print(temp)
        wait = convertToWords(temp)
        print(wait)
        waiting = {
            'clinic_name' : waitTimes[i][0],
            'wait_time' : wait,
            "color": colors[waitTimes[i][0]]
        }
        times.append(waiting)

    return render_template("index.html", names = names, times = times)

def convertToWords(time):
    if(time == "open"):
        return "open"
    hr = time[1:2]
    min = time[3:]
    return hr + " hour(s)" + " and " + min + " min(s)"


def checkChain(n, dat):
    for j in range(0, len(dat)):
        if dat[j][0] == n:
            n = dat[j][1]
            return checkChain(n, dat)
        else:
            return n
def hmtos(tim):
    h = int(tim[0:2])
    m = int(tim[3:5])
    s = h*3600+m*60
    return int(s)

def stohm(tim):
    h = str(tim//3600).zfill(2)
    m = str((tim%3600)//60).zfill(2)
    return (h+":"+m)

def findWaitTime(data, clinicNames):
    curTime = time.strftime("%H:%M", time.localtime())
    groups = []
    for i in range(0, len(clinicNames)):
        groups.append([])
        for j in range(0, len(data)):
            if data[j][4] == clinicNames[i]:
                groups[i].append(data[j])
    stats = []
    for i in range(0, len(clinicNames)):
        dat = groups[i]
        best = "00:00"
        besti = 0
        for j in range(0, len(dat)):
            if hmtos(dat[j][0]) > hmtos(best) and hmtos(dat[j][0]) < hmtos(curTime):
                best = dat[j][0]
                besti = j

        n = dat[besti][1]
        if hmtos(n) <= hmtos(curTime):
            status = "open"
        elif len(dat) == 1 and hmtos(n) > hmtos(curTime):
            status = stohm(hmtos(n)-hmtos(curTime))
        else:
            n = checkChain(n, dat)
            status = stohm(hmtos(n) - hmtos(curTime))
        stats.append([clinicNames[i], status])
    print(stats)
    return stats
if __name__ == "__main__":
    pyredb.WaitNoMore().start()
    app.run()



