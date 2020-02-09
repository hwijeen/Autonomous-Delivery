from collections import defaultdict


def read_lines_without_header(fpath):
    return [l.strip() for l in open(fpath).readlines()[1:]]

def make_travel_time(lines):
    times = defaultdict(dict)
    for line in lines:
        from_, to, time = line.split(',')
        times[from_][to] = float(time)
    return times

def make_turn_time(lines):
    times = dict()
    for line in lines:
        at, time = line.split(',')
        times[at] = float(time)
    return times

def read_time_files(clock_fpath, counterclock_fpath, turn_fpath):
    clock_lines = read_lines_without_header(clock_fpath)
    counterclock_lines = read_lines_without_header(counterclock_fpath)
    turn_lines = read_lines_without_header(turn_fpath)

    clock_times = make_travel_time(clock_lines)
    counterclock_times = make_travel_time(counterclock_lines)
    turn_times = make_turn_time(turn_lines)
    return clock_times, counterclock_lines, turn_times
