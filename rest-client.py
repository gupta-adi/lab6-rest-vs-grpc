#!/usr/bin/env python3

from __future__ import print_function

import requests
import json
import time
import base64
import jsonpickle
import random
import argparse


def doRawImage(addr, debug=False):

    # prepare headers for http request
    headers = {'content-type': 'image/jpeg'}

    img = open('Flatirons_Winter_Sunrise_edit_2.jpg', 'rb').read()

    # send http request with image and receive response
    image_url = addr + '/api/rawimage'
    response = requests.post(image_url, data=img, headers=headers)

    if debug:
        print("Response is", response)
        print(json.loads(response.text))


def doAdd(addr, debug=False):

    headers = {'content-type': 'application/json'}

    # send http request with image and receive response
    add_url = addr + "/api/add/5/10"
    response = requests.post(add_url, headers=headers)

    if debug:
        print("Response is", response)
        print(json.loads(response.text))



def doDotProduct(addr, debug=False):
    a = [random.random() for _ in range(100)]
    b = [random.random() for _ in range(100)]

    data = {
        'a': a,
        'b': b
    }

    response = requests.post(
        addr + '/api/dotproduct',
        json=data,
        timeout=30
    )

    response.raise_for_status()

    result = response.json()

    expected = sum(x * y for x, y in zip(a, b))

    assert abs(result['dotproduct'] - expected) < 1e-5

    if debug:
        print(result)




def doJsonImage(addr, debug=False):
    with open(
        'Flatirons_Winter_Sunrise_edit_2.jpg',
        'rb'
    ) as file:
        img = file.read()

    encoded = base64.b64encode(img).decode('utf-8')

    data = {
        'image': encoded
    }

    response = requests.post(
        addr + '/api/jsonimage',
        json=data,
        timeout=60
    )

    response.raise_for_status()

    result = response.json()

    assert result['width'] > 0
    assert result['height'] > 0

    if debug:
        print(result)



# ---------------------------------------------------------
# Parse command-line arguments
# ---------------------------------------------------------

parser = argparse.ArgumentParser(
    description='REST client for measuring server operations'
)

parser.add_argument(
    'host',
    help='IP address or hostname of the REST server'
)

parser.add_argument(
    'cmd',
    choices=['add', 'rawImage', 'dotProduct', 'jsonImage'],
    help='Operation to perform'
)

parser.add_argument(
    'reps',
    type=int,
    help='Number of repetitions for measurement'
)

parser.add_argument(
    '-p', '--port',
    type=int,
    default=5000,
    help='Server port (default: 5000)'
)

parser.add_argument(
    '-d', '--debug',
    action='store_true',
    help='Print the response from the server'
)

args = parser.parse_args()


# ---------------------------------------------------------
# Build server address
# ---------------------------------------------------------

addr = f"http://{args.host}:{args.port}"

print(f"Running {args.reps} reps against {addr}")


# ---------------------------------------------------------
# Perform requested operation
# ---------------------------------------------------------

if args.cmd == 'rawImage':

    start = time.perf_counter()

    for x in range(args.reps):
        doRawImage(addr, debug=args.debug)

    delta = ((time.perf_counter() - start) / args.reps) * 1000
    print("Took", delta, "ms per operation")


elif args.cmd == 'add':

    start = time.perf_counter()

    for x in range(args.reps):
        doAdd(addr, debug=args.debug)

    delta = ((time.perf_counter() - start) / args.reps) * 1000
    print("Took", delta, "ms per operation")


elif args.cmd == 'jsonImage':

    start = time.perf_counter()

    for x in range(args.reps):
        doJsonImage(addr, debug=args.debug)

    delta = ((time.perf_counter() - start) / args.reps) * 1000
    print("Took", delta, "ms per operation")


elif args.cmd == 'dotProduct':

    start = time.perf_counter()

    for x in range(args.reps):
        doDotProduct(addr, debug=args.debug)

    delta = ((time.perf_counter() - start) / args.reps) * 1000
    print("Took", delta, "ms per operation")

