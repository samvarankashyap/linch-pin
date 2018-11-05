#!/usr/bin/env python

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

from .InventoryFilter import InventoryFilter


class NummyInventory(InventoryFilter):

    def get_hostnames(self, topo):
        hostnames = []
        for group in topo['nummy_res']:
            for host in group['hosts']:
                hostnames.append(host)
        return hostnames


    def get_host_ips(self, topo):
        return self.get_hostnames(topo)


    def get_inventory(self, topo, layout):
        if len(topo['nummy_res']) == 0:
            return ""
        inven_hosts = self.get_hostnames(topo)
        # adding sections to respective host groups
        host_groups = self.get_layout_host_groups(layout)
        self.add_sections(host_groups)
        # set children for each host group
        self.set_children(layout)
        # set vars for each host group
        self.set_vars(layout)
        # add ip addresses to each host
        self.add_ips_to_groups(inven_hosts, layout)
        self.add_common_vars(host_groups, layout)
        output = StringIO()
        self.config.write(output)
        return output.getvalue()
