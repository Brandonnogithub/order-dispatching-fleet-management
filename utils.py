import csv
import random


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


def random_tuple(a, b):
    '''
    random sample from (0,0) to (a-1,b-1)
    '''
    return (random.randint(0,a-1), random.randint(0,b-1))


def random_tuple(a, b, n):
    '''
    random sample from (0,0) to (a-1,b-1)
    n is sample number
    '''
    if n < 1:
        raiseError("random number " + str(n))
    if n == 1:
        return random_tuple(a, b)
    else:
        res = []
        for i in range(n):
            res.append(random_tuple(a, b))
        return res