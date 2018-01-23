"""
  Copyright (c) 2012, Yahoo! Inc. All rights reserved.
  Code licensed under the BSD License:
  http://yuilibrary.com/license/
"""

import os
from .attrdict import attrdict

# var fs = require('fs'),
#     path = require('path');

# /* istanbul ignore next */
# var exists = fs.exists || path.exists;

def emptyItem():
  return attrdict({
    "title": "unknown",
    "file": "unkown",
    "lines": attrdict({
      "found": 0,
      "hit": 0,
      "details": [],
    }),
    "functions": attrdict({
      "hit": 0,
      "found": 0,
      "details": [],
    }),
    "branches": attrdict({
      "hit": 0,
      "found": 0,
      "details": [],
    }),
  })

def walkFile(lcov):
  data = []
  item = emptyItem()

  for line in lcov.split('\n'):
    line = line.strip()

    allparts = line.split(':')
    parts = [allparts[:1][0], ":".join(allparts[1:])]
    check = parts[0].upper()

    if check == 'TN':
      item.title = parts[1].strip()

    if check == 'SF':
      item.file = ":".join(parts[1:]).strip()

    if check == 'FNF':
      item.functions.found = float(parts[1].strip())

    if check == 'FNH':
      item.functions.hit = float(parts[1].strip())

    if check == 'LF':
      item.lines.found = float(parts[1].strip())

    if check == 'LH':
      item.lines.hit = float(parts[1].strip())

    if check == 'DA':
      lines = parts[1].split(',')
      item.lines.details.append({
        "line": float(lines[0]),
        "hit": float(lines[1]),
      })

    if check == 'FN':
      fn = parts[1].split(',')
      item.functions.details.append({
        "name": fn[1],
        "line": float(fn[0]),
        "hit": 0,
      })

    if check == 'FNDA':
      fn = parts[1].split(',')
      i = -1
      for x in item.functions.details:
        i = i + 1
        if x['name'] == fn[1] and x['hit'] == 0:
          break

      if i < len(item.functions.details):
        item.functions.details[i]['hit'] = float(fn[0])

    if check == 'BRDA':
      fn = parts[1].split(',')
      if fn[3] == '-':
        taken = 0
      else:
        taken = float(fn[3])

      item.branches.details.append({
        "line": float(fn[0]),
        "block": float(fn[1]),
        "branch": float(fn[2]),
        "taken": taken,
      })

    if check == 'BRF':
      item.branches.found = float(parts[1])

    if check == 'BRH':
      item.branches.hit = float(parts[1])

    if 'end_of_record' in line:
      data.append(item)
      item = emptyItem()

  return data



