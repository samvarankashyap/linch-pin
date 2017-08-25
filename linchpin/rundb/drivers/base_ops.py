#!/usr/bin/python
# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod
# action manager abstract class to be implemented by all
# action managers
class BaseOps(object):
    __metaclass__ = ABCMeta
    
    @abstractmethod
    def get_runlist(self):
        pass

    @abstractmethod
    def create_resource_list(self, runid, resource_type):
        pass

    @abstractmethod
    def delete_resource_list(self, runid, resource_type):
        pass

    @abstractmethod
    def append_to_resource_list(self, runid, provider_name):
        pass
