from typing import List, Any

from flask import Blueprint, render_template
from carcollect.db import get_db

import random
import time

# define blueprint
bp = Blueprint('sort', __name__, url_prefix='/sort')

# error list
ERRORS: List[str] = []


# get full table from db
def get_data(table='result'):
    # get data from db
    db = get_db()
    db_data = db.execute(
        'SELECT * FROM ?', table
    ).fetchall()
    data = []

    # convert data to a simple dictionary
    for item in db_data:
        row = {
            'filename': item[0],
            'severity': item[1],
            'probability': item[2]
        }
        data.append(row)

    # return data in dictionary
    return data


# Sorting test called by url to test functionality (temp)
@bp.route('/test')
def test_sorting():
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
            sort_start = time.clock()
            sort(data, 0, n - 1)
            sort_end = time.clock()
            completion_message = 'Test successful! Sorted data by {}. The list took {} seconds to sort. Array length: ' \
                                 '{}.' \
                .format(sort_by, sort_end - sort_start, n)
        except TypeError as e:
            ERRORS.append(str(e))
    else:
        completion_message = 'list is empty and therefor does not need sorting.'

    return render_template('sort/sort_test.html', errors=ERRORS, message=completion_message, result=data)


# Main sorting function
def sort(data, low, high):
    if not all(isinstance(x, int) for x in data):
        raise TypeError('Not all values in this collection are of type: int')
    quicksort(data, low, high)


# partition function
def partition(data, low, high):
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


# The actual sorting starts here
def quicksort(data, low, high):
    if low < high:
        try:
            pi = partition(data, low, high)
        except RecursionError:
            ERRORS.append("Recursion limit exceeded")

        # Separately sort elements before
        # partition and after partition
        quicksort(data, low, pi - 1)
        quicksort(data, pi + 1, high)
