#!/usr/bin/env python

def filter_ibm_vs_ids(topo_outputs):
    instance_ids = []
    for item in topo_outputs:
        instance = item.get("instance")
        if type(instance) is list:
            print(instance)
            for ins in instance:
                instance_ids(ins.get("id"))
        else:
            instance_ids.append(instance.get("id"))
    return instance_ids

class FilterModule(object):
    ''' A filter to get ids of ibm_vs_cloud '''
    def filters(self):
        return {
            'filter_ibm_vs_ids': filter_ibm_vs_ids
        }
