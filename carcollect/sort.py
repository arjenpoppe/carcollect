from typing import List, Any

from flask import Blueprint, render_template
from carcollect.db import get_db

import random
import time

# define blueprint
bp = Blueprint('sort', __name__, url_prefix='/sort')

# error list
ERRORS: List[str] = []


def get_data(table='result'):
    """Collect all data from database table and converts it to dict
    
    Keyword Arguments:
        table {str} -- table name (default: {'result'})
    
    Returns:
        dict -- all table data
    """
    db = get_db()
    db_data = db.execute(
        'SELECT * FROM ?', table
    ).fetchall()
    data = []

    # convert data to a simple dictionary
    to_dict(data, db_data)

    return data


def to_dict(data, db_data):
    """converts sqlite.objects to dict
    
    Arguments:
        data {list} -- [description]
        db_data {SQLITE.OBJECT} -- raw database data
    """
    for item in db_data:
        row = {
            'filename': item[0],
            'severity': item[1],
            'probability': item[2]
        }
        data.append(row)


@bp.route('/test')
def test_sorting():
    """Method that tests the performance of the sorting process
    
    Returns:
        template -- view with results
    """
    # get dummy data
    data = [random.randrange(10000000) for _ in range(100)]
    # data = [45, 567, 3, 67, 'ertert']
    # data = get_data()

    completion_message = ''

    # check if data is not empty and consists of integers only
    if data:
        # sort data
        n = len(data)
        sort_by = 'probability'

        # shuffle data to prevent worst case scenario
        random.shuffle(data)

        # making sure the correct result and/or errors are shown
        try:
            sort_start = time.process_time()
            sort(data, 0, n - 1)
            sort_end = time.process_time()
            completion_message = 'Test successful! Sorted data by {}. The list took {} seconds to sort. Array length: ' \
                                 '{}.' \
                .format(sort_by, sort_end - sort_start, n)
        except TypeError as e:
            ERRORS.append(str(e))
    else:
        completion_message = 'list is empty and therefor does not need sorting.'

    return render_template('sort/sort_test.html', errors=ERRORS, message=completion_message, result=data)


def sort(data, low, high):
    """checks data formatting then starts quicksort process
    
    Arguments:
        data {[type]} -- [description]
        low {[type]} -- [description]
        high {[type]} -- [description]
    
    Raises:
        TypeError: [description]
    """
    if not all(isinstance(x, int) for x in data):
        raise TypeError('Not all values in this collection are of type: int')
    quicksort(data, low, high)


def partition(data, low, high):
    """handles the partitioning part for quicksort. called by quicksort()
    
    Arguments:
        data {simple collection} -- data to be sorted
        low {int} -- lowest index in collection
        high {int} -- highest index in collection
    
    Returns:
        int -- the position index of the pivot point in the array
    """
    # set the index for the lower element
    i = (low - 1)

    # pick last value as pivot point
    pivot = data[high]

    # iterate over data to find location of pivot
    for j in range(low, high):

        # If current element is smaller than or eq to pivot increment index then swap index and j
        if data[j] <= pivot:
            i = i + 1
            data[i], data[j] = data[j], data[i]

    # move the pivot to its correct index
    data[i + 1], data[high] = data[high], data[i + 1]

    # return pivot index
    return i + 1


def quicksort(data, low, high):
    """main quicksort method, gets claled by sort()
    
    Arguments:
        data {simple collection} -- data to be sorted
        low {int} -- lowest index in collection
        high {int} -- highest index in collection
    """
    if low < high:
        try:
            pi = partition(data, low, high)
        except RecursionError:
            ERRORS.append("Recursion limit exceeded")

        # Separately sort elements before
        # partition and after partition
        quicksort(data, low, pi - 1)
        quicksort(data, pi + 1, high)
