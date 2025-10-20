import time

clicks = 1
click_intervals = []

def time_difference(start):
    return time.time() - start

def average(sequence):
    sum = 0
    for item in sequence:
        sum += item
    return sum / len(sequence)

def bpm():
    return round(60 / average(click_intervals), 3)

def duration():
    dur_secs = sum(click_intervals)
    whole_mins = dur_secs // 60
    dur_secs -= whole_mins * 60
    if whole_mins == 0:
        return "%s seconds" % (str(round(dur_secs, 3)))
    elif whole_mins == 1:
        return "1 minute, %s seconds" % (str(round(dur_secs, 3)))
    else:
        return "%s minutes, %s seconds" % (str(round(whole_mins, 3)), str(round(dur_secs, 3)))

def print_stats():
    print ("Previous click duration: %s miliseconds" % (str(int(1000 * round(click_intervals[len(click_intervals) - 1], 3)))))
    print ("Average click duration: %s miliseconds" % (str(int(1000 * round(average(click_intervals), 3)))))
    print ("Maximum click duration: %s miliseconds" % (str(int(1000 * round(max(click_intervals), 3)))))
    print ("Minimum click duration: %s miliseconds" % (str(int(1000 * round(min(click_intervals), 3)))))
    print ("Range: %s miliseconds" % (str(int(1000 * round(max(click_intervals) - min(click_intervals), 3)))))
    print ("Clicks: %s" % (str(clicks)))
    print ("Duration: %s" % (duration()))
    print ()

def run_input_mode(stat):
    global clicks
    finished = False
    current_time = time.time()
    input("First click recieved... ")
    click_intervals.append(time_difference(current_time))
    while not finished:
        current_time = time.time()
        print()
        if stat:
            print_stats()
        if not input("%s BPM " % (bpm())).lower():
            click_intervals.append(time_difference(current_time))
            clicks += 1
        else:
            finished = True
    print ()
    print ("Average click duration: %s miliseconds" % (str(int(1000 * round(average(click_intervals), 3)))))
    print ("Maximum click duration: %s miliseconds" % (str(int(1000 * round(max(click_intervals), 3)))))
    print ("Minimum click duration: %s miliseconds" % (str(int(1000 * round(min(click_intervals), 3)))))
    print ("Range: %s miliseconds" % (str(int(1000 * round(max(click_intervals) - min(click_intervals), 3)))))
    print ("Clicks: %s" % (str(clicks)))
    print ("Duration: %s" % (duration()))
    print ()

def run_tempo_mode(tempo):
    count = 1
    while "Hello".upper() == "HELLO":
        print(f"This message is printing at {tempo} BPM and I have printed {count} messages so far. Press ctrl + c to terminate")
        count += 1
        time.sleep(60 / tempo)

mode = input('While listening to the song, press "enter" to the beat. When finished, enter "done" in the terminal. If you want statistical mode, enter "stat". If you want to see a certain tempo, enter "tempo". Begin when ready: ').lower()
if mode == "stat" or mode != "tempo":
    run_input_mode(mode == "stat")
else:
    run_tempo_mode(float(input('Enter a BPM rate to see how it is paced: ')))