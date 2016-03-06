# Auther: Michael Ciesla <miciesla@cisco.com>
# Date: 3 Mar 2016

import time
from acitoolkit.acitoolkit import *
from Queue import Queue
from vmware import DVS


# Create the Tenant
tenant = Tenant('BB-9')


# Create the Application Profile
app = AppProfile('Universe-App', tenant)


# Create the EPG
web_client_EPG = EPG('web-client', app)
load_balancer_EPG = EPG('load-balancer', app)
web_server_EPG = EPG('web-server', app)


# Create a VRF and Bridge Domain
context = Context('vrf-1', tenant)
bd = BridgeDomain('bd-1', tenant)
bd.add_context(context)
bd.set_arp_flood('yes')
bd.set_unknown_mac_unicast('flood')


# Place the EPG in the BD
web_client_EPG.add_bd(bd)
load_balancer_EPG.add_bd(bd)
web_server_EPG.add_bd(bd)


# Define a contract with a single entry
client_lb_CON = Contract('client_lb', tenant)
entry1 = FilterEntry('http',
                     applyToFrag='no',
                     arpOpc='unspecified',
                     dFromPort='80',
                     dToPort='80',
                     etherT='ip',
                     prot='tcp',
                     sFromPort='unspecified',
                     sToPort='unspecified',
                     tcpRules='unspecified',
                     parent=client_lb_CON)


# Provide the contract from 1 EPG and consume from the other
load_balancer_EPG.provide(client_lb_CON)
web_client_EPG.consume(client_lb_CON)


# Define a contract with a single entry
lb_server_CON = Contract('lb_server', tenant)
entry1 = FilterEntry('http',
                     applyToFrag='no',
                     arpOpc='unspecified',
                     dFromPort='80',
                     dToPort='80',
                     etherT='ip',
                     prot='tcp',
                     sFromPort='unspecified',
                     sToPort='unspecified',
                     tcpRules='unspecified',
                     parent=lb_server_CON)


# Provide the contract from 1 EPG and consume from the other
load_balancer_EPG.consume(lb_server_CON)
web_server_EPG.provide(lb_server_CON)


# Get the APIC login credentials
description = 'acitoolkit tutorial application'
creds = Credentials('apic', description)
args = creds.get()

# Login to APIC and push the config
session = Session(args.url, args.login, args.password)
session.login()

# Get the Physical & VMM domains
dom = EPGDomain.get_by_name(session, 'Networks')
vmmdom = EPGDomain.get_by_name(session, 'vmm')

# Attached EPGs to the VMM domain
web_client_EPG.add_infradomain(dom)
load_balancer_EPG.add_infradomain(vmmdom)
web_server_EPG.add_infradomain(vmmdom)

# Attach VLAN17 to interface 17 in leaf101
if1 = Interface('eth', '1', '101', '1', '17')
vlan17_on_if1 = L2Interface('vlan17_on_if1', 'vlan', '17')
vlan17_on_if1.attach(if1)

# Attach the EPG to the VLANs
web_client_EPG.attach(vlan17_on_if1)

# Push the tenant configuration to APIC
resp = tenant.push_to_apic(session)
if resp.ok:
    print 'Success'

# Print what was sent
print 'Pushed the following JSON to the APIC'
print 'URL:', tenant.get_url()
print 'JSON:', tenant.get_json()

# Migrate Universe-App VM NICs to ACI DVS port-profiles in vSphere.
# Also connect the VM NICs.
time.sleep(5)
DVS.dvs_aci()
