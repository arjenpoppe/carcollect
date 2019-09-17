import functools
import os
import click

from flask import (
    Blueprint, flash, redirect, render_template, request, url_for, current_app, send_from_directory
)
from flask.cli import with_appcontext
from werkzeug.utils import secure_filename

import matplotlib.pyplot as plt
from scipy import arange
from scipy.io import wavfile as wav
from scipy.fftpack import fft, fftfreq
import numpy as np

from carcollect.db import get_db

bp = Blueprint('sort', __name__, url_prefix='/sort')



def get_data():
    db = get_db()
    data = db.execute(
        'SELECT * FROM result'
    ).fetchall()
    return data


@bp.route('/test')
def sort_data():
    data = get_data()
    # data = db_data
    n = len(data)
    sort_by = 'probability'
    quicksort(data, sort_by, 0, n-1)
    print("Sorted array is:")
    for i in range(n):
        print('{}\t{}\t{}'.format(data[i]['filename'], data[i]['severity'], data[i]['probability']),)


# Python program for implementation of Quicksort Sort

# This function takes last element as pivot, places
# the pivot element at its correct position in sorted
# array, and places all smaller (smaller than pivot)
# to left of pivot and all greater elements to right
# of pivot
def partition(data, sort_by, low, high):
    i = (low-1)  # index of smaller element
    pivot = data[high][sort_by]  # pivot

    for j in range(low, high):

        # If current element is smaller than or
        # equal to pivot
        if data[j][sort_by] <= pivot:
            # increment index of smaller element
            i = i + 1
            data[i], data[j] = data[j], data[i]

    data[i + 1], data[high] = data[high], data[i + 1]
    return (i + 1)


# The main function that implements QuickSort
# data[] --> Array to be sorted,
# column --> What column to sort on
# low  --> Starting index,
# high  --> Ending index

# Function to do Quick sort
def quicksort(data, sort_by, low, high):
    if low < high:
        # pi is partitioning index, arr[p] is now
        # at right place
        pi = partition(data, sort_by, low, high)

        # Separately sort elements before
        # partition and after partition
        quicksort(data, sort_by, low, pi - 1)
        quicksort(data, sort_by, pi + 1, high)


