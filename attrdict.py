"""
  Copyright (c) 2012, Yahoo! Inc. All rights reserved.
  Code licensed under the BSD License:
  http://yuilibrary.com/license/
"""

class attrdict(dict):
  def __init__(self, *args, **kwargs):
    dict.__init__(self, *args, **kwargs)
    self.__dict__ = self


