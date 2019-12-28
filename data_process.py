import os
import csv
import tarfile
import tempfile
import threading
from pathlib import Path


lock = threading.Lock()


def raiseError(content=""):
    raise Exception(content)


def load_csv(csv_path, select_list=None, headline=False):
    '''
    load csv data into list
    headline: whether there is a headline
    '''
    res = []
    with open(csv_path, 'r', encoding="utf8", newline="") as f_csv:
        if headline:
            reader = csv.DictReader(f_csv)
        else:
            reader = csv.reader(f_csv)
        if select_list:
            for row in reader:
                temp_row = []
                for index in select_list:
                    temp_row.append(row[index])
                res.append(temp_row)
        else:
            for row in reader:
                res.append(row)
    return res


def write_csv(contents, csv_path, head_row=None):
    '''write data into csv file. contents is a list. see the formation in load_csv()'''
    with open(csv_path, 'w', encoding="utf8", newline="") as f_csv:
        writer = csv.writer(f_csv)
        if head_row is not None:
            writer.writerow(head_row)
        writer.writerows(contents)


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
    drivers = set()
    for _, _, files in os.walk(path_dir):
        for file_name in files:
            if file_name[0] != "g":
                continue
            temp_path = os.path.join(path_dir, file_name)
            content = load_csv(temp_path, select_list=[0])
            for row in content:
                drivers.add(row[0])
            print(len(drivers))
    print(len(drivers)) # 1181180


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
        for row in content:
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


if __name__ == "__main__":
    # extract_data()
    # count_n_drivers()
    count_driver_thread()