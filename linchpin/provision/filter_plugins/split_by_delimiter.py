#!/usr/bin/env python
def split_by_delimiter(content, delimeter=","):
    return content.split(delimeter)


class FilterModule(object):
    ''' A filter to split strings into list '''
    def filters(self):
        return {
            'split_by_delimiter': split_by_delimiter
        }
