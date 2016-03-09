#!/usr/bin/env python

# Auther: Michael Ciesla <miciesla@cisco.com>
# Date: 28 Feb 2016

from acitoolkit.acitoolkit import *
from Queue import Queue
import requests


starwars_characters = ['Darth-Vader','Luke-Skywalker','Yoda','Boba-Fett',
                        'Supreme-Leader-Snoke','Han-Solo','Princess-Leia','R2-D2','Rey',
                        'The-Emperor','Darth-Maul','Padma-Amidala','C-3PO',
                        'Jar-Jar-Binks','Jabba-the-Hutt','Obi-Wan-Kenobi','Captain-Phasma',
                        'Clone-Trooper','Lando-Calrissian','Count-Dooku','Finn','Sabe',
                        'Jango-Fett','Qui-Gon-Jinn','Mace-Windu','Shmi-Skywalker']

# Get the APIC login credentials
description = 'acitoolkit tutorial application'
creds = Credentials('apic', description)
args = creds.get()

# Login to APIC and push the config
session = Session(args.url, args.login, args.password)
session.login()

# Init for validation
starwars_validation = 0

for hero in starwars_characters:
    # Create the Tenant
    tenant = Tenant(hero)

    # Create the Application Profile
    app = AppProfile('universe', tenant)

    # Create the EPG
    web_client_EPG = EPG('web-client', app)
    load_balancer_EPG = EPG('load-balancer', app)
    web_server_EPG = EPG('web-server', app)


    # Create a Context and BridgeDomain
    context = Context('vrf-1', tenant)
    bd = BridgeDomain('bd-1', tenant)
    bd.add_context(context)

    # Place the EPG in the BD
    web_client_EPG.add_bd(bd)
    load_balancer_EPG.add_bd(bd)
    web_server_EPG.add_bd(bd)


    # Define a contract with a single entry
    client_lb_CON = Contract('client_lb', tenant)
    entry1 = FilterEntry('tcp-dst-5000',
                        applyToFrag='no',
                        arpOpc='unspecified',
                        dFromPort='5000',
                        dToPort='5000',
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
    entry1 = FilterEntry('tcp-dst-80',
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



    # Get the VMM domain
    vmmdom = EPGDomain.get_by_name(session, 'vmm')

    # Attached EPGs to the VMM domain
    web_client_EPG.add_infradomain(vmmdom)
    load_balancer_EPG.add_infradomain(vmmdom)
    web_server_EPG.add_infradomain(vmmdom)

    resp = tenant.push_to_apic(session)
    if resp.ok:
        print 'Success'
        spark_post = requests.post('https://api.ciscospark.com/v1/webhooks/incoming/Y2lzY29zcGFyazovL3VzL1dFQkhPT0svYTg5N2QxMDEtMWQ5ZC00ZTA0LThkYzEtNzQwOTdmMmYyZDhm', data = {'text': hero+' has joined the ACI fabric!'})
        starwars_validation += 1
        print 'Length is ',len(starwars_characters)
        print 'Current validation is ',starwars_validation
        if starwars_validation == len(starwars_characters):
            print 'Validation succeeded.  Sending outbound text'
            tropo_post = requests.get('https://api.tropo.com/1.0/sessions?token=51697a667264676c41756c54784d58534e686c786364734b62455a4765744d4d46756458554d43514a515574&msg=The Force is with you! All Star Wars ACI is provisioned!&numberToDial=+61413900700&action=create')

    # Print what was sent
    print 'Pushed the following JSON to the APIC'
    print 'URL:', tenant.get_url()
    print 'JSON:', tenant.get_json()
