#!/usr/bin/env python
"""
Written by Reubenur Rahman
Github: https://github.com/rreubenur/

This code is released under the terms of the Apache 2
http://www.apache.org/licenses/LICENSE-2.0.html

Example script to change the network of the Virtual Machine NIC

"""

import atexit

#from tools import cli
from tools import tasks
from pyVim import connect
from pyVmomi import vim, vmodl


def get_obj(content, vimtype, name):
    """
     Get the vsphere object associated with a given text name
    """
    obj = None
    container = content.viewManager.CreateContainerView(content.rootFolder,
                                                        vimtype, True)
    for view in container.view:
        if view.name == name:
            obj = view
            break
    return obj



def main():
    HOST = '10.67.16.198'
    USER = 'root'
    PASSWORD = '@dm1nC1sc1'
    PORT = '443'
    VM_UUIDS = ['423ae3f6-bd80-31ad-1d30-55dbbd5e4c35',
                '423aa622-08dc-5560-39dd-01c13e7a550b',
                '423af213-8013-f397-0114-bec8172ec008']

    LB = '423af213-8013-f397-0114-bec8172ec008'

    NETWORK_NAME = 'BB-9|Universe-App|web-server'
    is_VDS = True

    try:
        service_instance = connect.SmartConnect(host=HOST,
                                                user=USER,
                                                pwd=PASSWORD,
                                                port=int(PORT))

        atexit.register(connect.Disconnect, service_instance)
        content = service_instance.RetrieveContent()

        for VM_UUID in VM_UUIDS :
            if VM_UUID == LB:
                NETWORK_NAME = 'BB-9|Universe-App|load-balancer'

            vm = content.searchIndex.FindByUuid(None, VM_UUID, True)
            # This code is for changing only one Interface. For multiple Interface
            # Iterate through a loop of network names.
            device_change = []
            for device in vm.config.hardware.device:
                if isinstance(device, vim.vm.device.VirtualEthernetCard):
                    nicspec = vim.vm.device.VirtualDeviceSpec()
                    nicspec.operation = \
                        vim.vm.device.VirtualDeviceSpec.Operation.edit
                    nicspec.device = device
                    nicspec.device.wakeOnLanEnabled = True

                    if not is_VDS:
                        nicspec.device.backing = \
                            vim.vm.device.VirtualEthernetCard.NetworkBackingInfo()
                        nicspec.device.backing.network = \
                            get_obj(content, [vim.Network], NETWORK_NAME)
                        nicspec.device.backing.deviceName = NETWORK_NAME
                    else:
                        print 'its a DVS'
                        network = get_obj(content,
                                          [vim.dvs.DistributedVirtualPortgroup],
                                          NETWORK_NAME)
                        dvs_port_connection = vim.dvs.PortConnection()
                        dvs_port_connection.portgroupKey = network.key
                        dvs_port_connection.switchUuid = \
                            network.config.distributedVirtualSwitch.uuid
                        nicspec.device.backing = \
                            vim.vm.device.VirtualEthernetCard. \
                            DistributedVirtualPortBackingInfo()
                        nicspec.device.backing.port = dvs_port_connection

                    nicspec.device.connectable = \
                        vim.vm.device.VirtualDevice.ConnectInfo()
                    nicspec.device.connectable.connected = True
                    nicspec.device.connectable.startConnected = True
                    nicspec.device.connectable.allowGuestControl = True
                    device_change.append(nicspec)
                    break

            config_spec = vim.vm.ConfigSpec(deviceChange=device_change)
            task = vm.ReconfigVM_Task(config_spec)
            tasks.wait_for_tasks(service_instance, [task])
            print "Successfully changed network"

    except vmodl.MethodFault as error:
        print "Caught vmodl fault : " + error.msg
        return -1

    return 0

# Start program
if __name__ == "__main__":
    main()
