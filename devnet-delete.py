#!/usr/bin/env python


# Auther: Michael Ciesla <miciesla@cisco.com>
# Date: 28 Feb 2016

import sys
import time
from acitoolkit.acitoolkit import *
from vmware import DVS


def main():
    """
    Main execution routine

    :return: None
    """

    # Detach Universe-App from ACI DVS port-groups.
    DVS.dvs_quarantine()
    time.sleep(5)

    # Take login credentials from the command line if provided
    # Otherwise, take them from your environment variables file ~/.profile
    description = 'Simple application that logs on to the APIC and displays all of the Tenants.'
    creds = Credentials('apic', description)
    args = creds.get()

    # Login to APIC
    session = Session(args.url, args.login, args.password)
    resp = session.login()
    if not resp.ok:
        print('%% Could not login to APIC')
        sys.exit(0)

    starwars = ['Kylo-Ren','Darth-Vader','Luke-Skywalker','Yoda','Boba-Fett',
                'Supreme-Leader-Snoke','Han-Solo','Princess-Leia','R2-D2','Rey',
                'The-Emperor','Darth-Maul','Chewbacca','Padma-Amidala','C-3PO',
                'Jar-Jar-Binks','Jabba-the-Hutt','Obi-Wan-Kenobi','Captain-Phasma',
                'Clone-Trooper','Lando-Calrissian','Count-Dooku','Finn','Sabe',
                'Jango-Fett','Qui-Gon-Jinn','Mace-Windu','Shmi-Skywalker','BB-9']

    # Download all of the tenants
    print("TENANT")
    print("------")

    tenants = Tenant.get(session)

    for tenant in tenants:
        for star in starwars:
            if star == tenant.name:
                print 'Removing tenant',tenant.name
                tenant.mark_as_deleted()
                resp = tenant.push_to_apic(session)
                if resp.ok:
                    print 'Success'
                print 'Pushed the following JSON to the APIC'
                print 'URL:', tenant.get_url()
                print 'JSON:', tenant.get_json()

if __name__ == '__main__':
    main()
