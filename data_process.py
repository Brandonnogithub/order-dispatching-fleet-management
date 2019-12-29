import os
import csv
import tarfile
import tempfile
import threading
import numpy as np
from pathlib import Path
from gps_utils import gcj02wgs84
from utils import write_csv, load_csv, raiseError


lock = threading.Lock()
base_time = 1477929720 - 75
time_step = 600     # 10 mins
POS_RANGE = [[103.89325, 30.547255], [104.20675, 30.852745]]  # some data out of range
total_removed = 0   # for threading method
N_GIRD_X = 15
D_GIRD_X = 0.0209
N_GRID_Y = 17
D_GIRD_Y = 0.01797
DAY = 1


def real_time(t, day):
    base = (day-1) * 86400
    return int((int(t) - base_time - base) / time_step)


def time_without_day(t):
    return int((int(t) - base_time) / time_step)


def extract_tar(path):
    date = Path(path).stem.split(".")[0]
    print(date)
    # tempdir = tempfile.mkdtemp()
    with tarfile.open(path, 'r:gz') as archive:
        archive.extractall("data/extracted")


def extract_data(path_dir="data/raw"):
    for _, _, files in os.walk(path_dir):
        for file_name in files:
            temp_path = os.path.join(path_dir, file_name)
            extract_tar(temp_path)


def count_n_drivers(path_dir="data/extracted"):
    res = []
    for _, _, files in os.walk(path_dir):
        for file_name in files:
            if file_name[0] != "g":
                continue
            drivers = set()
            temp_path = os.path.join(path_dir, file_name)
            content = load_csv(temp_path, select_list=[0])
            last = None
            for row in content:
                if row[0] == last:
                    continue
                else:
                    last = row[0]
                    drivers.add(row[0])
            print(len(drivers))
            res.append(len(drivers))
    # print(len(drivers)) # 1181180
    print(res)


class CountDriverThread(threading.Thread):
    def __init__(self, path=None, driver_pool=None):
        super().__init__()
        self.path = path
        self.driver_pool = driver_pool

    def run(self):
        if self.path is None:
            return
        if self.driver_pool is None:
            raiseError("Need driver pool")

        print("%s starts..." % self.name)

        content = load_csv(self.path, select_list=[0])
        drivers = set()
        last = None
        for row in content:
            if row[0] == last:
                continue
            else:
                last = row[0]
                drivers.add(row[0])
        # update
        lock.acquire()
        self.driver_pool.update(drivers)
        lock.release()

        print("%s finished! There are %d drivers." %(self.name, len(drivers)))


def count_driver_thread(n_thread=12, path_dir="data/extracted"):
    drivers = set()
    thread_pool = [CountDriverThread(driver_pool=drivers) for _ in range(n_thread)]
    count = 0
    for _, _, files in os.walk(path_dir):
        for file_name in files:
            if file_name[0] != "g":
                continue
            temp_path = os.path.join(path_dir, file_name)
            thread_pool[count].path = temp_path
            count += 1
            if count >= n_thread:
                for i in thread_pool:
                    i.start()
                for i in thread_pool:
                    i.join()
                # rebuild thread pool
                thread_pool = [CountDriverThread(driver_pool=drivers) for _ in range(n_thread)]
                count = 0
    # start the left threads
    for i in range(count):
        thread_pool[i].start()
    for i in range(count):
        thread_pool[i].join()
    print(len(drivers)) # 1181180


def find_time_duratin(path="data/extracted/order_20161104"):
    '''
    return the min start time and max start time in one day 
    '''
    content = load_csv(path, select_list=[1,2])
    max_time = 0
    min_time = int(content[0][0])
    # min_time = 1477929720
    max_dur = 0
    for i in range(len(content)):
        content[i] = list(map(int, content[i]))
        if content[i][0] < min_time:
            min_time = content[i][0]
        if content[i][0] > max_time:
            max_time = content[i][0]
        if content[i][1] - content[i][0] > max_dur:
            max_dur = content[i][1] - content[i][0]
    # print(min_time)
    # print(max_time)
    # d = max_time - min_time
    # d = d / 3600
    # print(d)
    # print(max_dur)
    return min_time, max_time


def find_time_zero(path_dir="data/extracted"):
    '''
    adjut all start and end time of each day with the base time. base time is the start time of the first day in record
    '''
    base = 1477929720
    res = []
    for _, _, files in os.walk(path_dir):
        for file_name in files:
            if file_name.startswith("order"):
                a, b = find_time_duratin(os.path.join(path_dir, file_name))
                a -= base
                b -= base
                res.append(a)
                res.append(b)
    print(res)


def adjust_time_zero():
    '''
    find the zero time of the first day
    '''
    timeline = [0, 86279, 86371, 172677, 172739, 259076, 259172, 345477, 345599, 431879, 431986, 518278, 518383, 604678, 604743, 691075, 691145, 777478, 777576, 863878, 863943, 950278, 950363, 1036677, 1036771, 1123077, 1123185, 1209476, 1209562, 1295878, 1295936, 1382279, 1382369, 1468674, 1468775, 1555079, 1555130, 1641477, 1641554, 1727879, 1727976, 1814277, 1814325, 1900679, 1900726, 1987078, 1987136, 2073477, 2073582, 2159878, 2159995, 2246277, 2246340, 2332677, 2332725, 2419077, 2419153, 2505479, 2505554, 2591878]
    assert len(timeline) == 30 *2, "wrong!"
    timeline = np.array(timeline)
    zero_time = 0
    for i in range(30):
        offset = min(0, timeline[i*2] - zero_time - 86400 * i)
        zero_time += offset
    for i in range(30):
        offset = max(0, timeline[i*2+1] - zero_time - 86400 * (i+1))
        assert offset == 0, "No solution!"
    print(zero_time)    # -75


def map_str2float(a):
    return list(map(float, a))


def map_float2int(a):
    return list(map(int, a))


def map_list(a):
    '''
    a is a list
    '''
    x, y = gcj02wgs84(a[0], a[1])
    z, k = gcj02wgs84(a[2], a[3])
    # if x > 110 or y < 25 or z > 110 or k < 25:
    #     print(a)
    #     raiseError()
    return [x, y, z, k]


def remove_baddata(c):
    def check_range(a):
        if a[0] >= POS_RANGE[0][0] and a[0] <= POS_RANGE[1][0]:
            if a[2] >= POS_RANGE[0][0] and a[2] <= POS_RANGE[1][0]:
                if a[1] >= POS_RANGE[0][1] and a[1] <= POS_RANGE[1][1]:
                    if a[3] >= POS_RANGE[0][1] and a[3] <= POS_RANGE[1][1]:
                        return True
        return False

    move_list = []
    for i in range(len(c)):
        if not check_range(c[i]):
            move_list.append(i)
    move_list.reverse()
    for i in move_list:
        del c[i]
    return len(move_list)


def find_pos_range(path_dir="data/extracted"):
    min_x_list = []
    max_x_list = []
    min_y_list = []
    max_y_list = []
    n_total = 0     # total moved
    for _, _, files in os.walk(path_dir):
        for file_name in files:
            if file_name.startswith("order"):
                temp_path = os.path.join(path_dir, file_name)
                content = load_csv(temp_path, select_list=[3,4,5,6])
                content = list(map(map_str2float, content))
                n_total += remove_baddata(content)
                content = np.array(list(map(map_list, content)))
                min_x = content[:,[0,2]].min()
                max_x = content[:,[0,2]].max()
                min_y = content[:,[1,3]].min()
                max_y = content[:,[1,3]].max()
                min_x_list.append(min_x)
                max_x_list.append(max_x)
                min_y_list.append(min_y)
                max_y_list.append(max_y)
    print(min(min_x_list))  # 103.0002196712431
    print(max(max_x_list))  # 120.35693932767293
    print(min(min_y_list))  # 22.86432541244561
    print(max(max_y_list))  # 40.144055627798586
    print(n_total)


class FindPosRangeThread(threading.Thread):
    def __init__(self, path=None, min_x_list=None, max_x_list=None, min_y_list=None, max_y_list=None):
        super().__init__()
        self.path = path
        self.min_x_list = min_x_list
        self.max_x_list = max_x_list
        self.min_y_list = min_y_list
        self.max_y_list = max_y_list

    def run(self):
        global total_removed
        if self.path is None:
            return

        print("%s starts..." % self.name)

        content = load_csv(self.path, select_list=[3,4,5,6])
        content = list(map(map_str2float, content))
        n = remove_baddata(content)
        lock.acquire()
        total_removed += n
        lock.release()
        content = np.array(list(map(map_list, content)))
        min_x = content[:,[0,2]].min()
        max_x = content[:,[0,2]].max()
        min_y = content[:,[1,3]].min()
        max_y = content[:,[1,3]].max()

        # update
        lock.acquire()
        self.min_x_list.append(min_x)
        self.max_x_list.append(max_x)
        self.min_y_list.append(min_y)
        self.max_y_list.append(max_y)
        lock.release()

        print("%s finished! There are %d removed." %(self.name, n))


def find_pos_range_thread(n_thread=12, path_dir="data/extracted"):
    min_x_list = []
    max_x_list = []
    min_y_list = []
    max_y_list = []
    thread_pool = [FindPosRangeThread(min_x_list=min_x_list, max_x_list=max_x_list,min_y_list=min_y_list,max_y_list=max_y_list) for _ in range(n_thread)]
    count = 0
    for _, _, files in os.walk(path_dir):
        for file_name in files:
            if not file_name.startswith("order"):
                continue
            temp_path = os.path.join(path_dir, file_name)
            thread_pool[count].path = temp_path
            count += 1
            if count >= n_thread:
                for i in thread_pool:
                    i.start()
                for i in thread_pool:
                    i.join()
                # rebuild thread pool
                thread_pool = [FindPosRangeThread(min_x_list=min_x_list, max_x_list=max_x_list,min_y_list=min_y_list,max_y_list=max_y_list) for _ in range(n_thread)]
                count = 0
    # start the left threads
    for i in range(count):
        thread_pool[i].start()
    for i in range(count):
        thread_pool[i].join()
    print(min(min_x_list))  # 103.0002196712431
    print(max(max_x_list))  # 120.35693932767293
    print(min(min_y_list))  # 22.86432541244561
    print(max(max_y_list))  # 40.144055627798586
    print(total_removed) # ?


class FindPosDisThread(threading.Thread):
    def __init__(self, path=None, distribution=None):
        super().__init__()
        self.path = path
        self.distribution = distribution    # (10, 14)

    def run(self):
        global total_removed
        if self.path is None:
            return

        print("%s starts..." % self.name)

        content = load_csv(self.path, select_list=[3,4,5,6])
        # str2float
        content = list(map(map_str2float, content))
        # gcj2wgs
        content = list(map(map_list, content))
        n = remove_baddata(content)
        lock.acquire()
        total_removed += n
        lock.release()
        content = np.array(content)
        content[:,[0,2]] -= 103.5
        content[:,[0,2]] /= 0.1
        content[:,[1,3]] -= 30.3
        content[:,[1,3]] /= 0.05
        content = list(map(map_float2int, content))
        tem_dis = np.zeros(self.distribution.shape)
        for row in content:
            tem_dis[row[0], row[1]] += 1
            tem_dis[row[2], row[3]] += 1
        # update
        lock.acquire()
        self.distribution += tem_dis
        lock.release()

        print("%s finished! There are %d removed." %(self.name, n))


def find_pos_dis_thread(n_thread=12, path_dir="data/extracted"):
    distribution = np.zeros([10,14])
    thread_pool = [FindPosDisThread(distribution=distribution) for _ in range(n_thread)]
    count = 0
    for _, _, files in os.walk(path_dir):
        for file_name in files:
            if not file_name.startswith("order"):
                continue
            temp_path = os.path.join(path_dir, file_name)
            thread_pool[count].path = temp_path
            count += 1
            if count >= n_thread:
                for i in thread_pool:
                    i.start()
                for i in thread_pool:
                    i.join()
                # rebuild thread pool
                thread_pool = [FindPosDisThread(distribution=distribution) for _ in range(n_thread)]
                count = 0
    # start the left threads
    for i in range(count):
        thread_pool[i].start()
    for i in range(count):
        thread_pool[i].join()
    print(distribution)     # see res in test.py
    print(total_removed)    # 16xx


def total_orders(path_dir="data/extracted"):
    n = 0
    for _, _, files in os.walk(path_dir):
        for file_name in files:
            if not file_name.startswith("order"):
                continue
            temp_path = os.path.join(path_dir, file_name)
            content = load_csv(temp_path, select_list=[3,4,5,6])
            n += len(content)
    print(n)    # 7065937


def wgs2gird(x, y):
    x = int((x - POS_RANGE[0][0]) / D_GIRD_X)
    y = int((y - POS_RANGE[0][1]) / D_GIRD_Y)
    return x, y


def map_order(a):
    '''
    a:[t_s, t_e, x1, y1, x2, y2] string list
    '''
    x, y = gcj02wgs84(a[2], a[3])
    # x, y = wgs2gird(x, y)
    z, k = gcj02wgs84(a[4], a[5])
    # z, k = wgs2gird(z, k)
    return [time_without_day(int(a[0])), time_without_day(int(a[1])), x, y, z, k]


def remove_baddata_order(c):
    def check_range(a):
        if a[2] >= POS_RANGE[0][0] and a[2] < POS_RANGE[1][0]:
            if a[4] >= POS_RANGE[0][0] and a[4] < POS_RANGE[1][0]:
                if a[3] >= POS_RANGE[0][1] and a[3] < POS_RANGE[1][1]:
                    if a[5] >= POS_RANGE[0][1] and a[5] < POS_RANGE[1][1]:
                        return True
        return False

    move_list = []
    for i in range(len(c)):
        if not check_range(c[i]):
            move_list.append(i)
    move_list.reverse()
    for i in move_list:
        del c[i]
    return len(move_list)


def map_grid(a):
    a[2], a[3] = wgs2gird(a[2], a[3])
    a[4], a[5] = wgs2gird(a[4], a[5])
    return a


def formalize_order_data(path_dir="data/extracted"):
    global DAY
    global total_removed
    all_orders = []
    for _, _, files in os.walk(path_dir):
        for file_name in files:
            if not file_name.startswith("order"):
                continue
            DAY = int(file_name[-2:])
            temp_path = os.path.join(path_dir, file_name)
            content = load_csv(temp_path, select_list=[1,2,3,4,5,6])
            # map trans time and pos
            content = list(map(map_order, content))
            # remove bad data
            total_removed += remove_baddata_order(content)
            # map pos to grid
            content = list(map(map_grid, content))
            # print(content[:10])
            # raiseError()
            all_orders += content
    write_csv(all_orders, "data/process/order_201611.csv")
    print(len(all_orders))
    print(total_removed)
    print("Finish!")


def map_str2int(a):
    return list(map(int, a))


def sort_orders(path_dir="data/process/order_201611.csv"):
    content = load_csv(path_dir)
    content = list(map(map_str2int, content))
    for i in range(len(content)):
        content[i][1] = max(content[i][1] - content[i][0], 1)
    content.sort(key=lambda x: x[0])
    write_csv(content, path_dir)


if __name__ == "__main__":
    # extract_data()
    # count_n_drivers()
    # count_driver_thread()
    # find_time_duratin()
    # find_time_zero()
    # adjust_time_zero()
    # find_pos_range()
    # find_pos_range_thread(6)
    # find_pos_dis_thread()
    # total_orders()
    # formalize_order_data()
    sort_orders()
    print("Finished!")
