#!/usr/bin/env python3
from collections import defaultdict
import os
import sqlite3
import sys


# Colours
BOLD = '\033[1m'
RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
ENDC = '\033[0m'


def main():
    # Obtain a search term if provided
    md5sums = False
    search = None
    if len(sys.argv) > 1:
        for arg in sys.argv[1:]:
            if arg in ['-h', '--help']:
                print(f'Usage: {__file__} [-h/--help] [-m/--md5sums] [<search>]')
                exit()
            elif arg in ['-m', '--md5sums']:
                md5sums = True
            else:
                search = arg

    # Connect to the Spitfire Audio Library Manager SQLite database
    try:
        conn = sqlite3.connect(os.path.join(
            os.path.expanduser('~'), 'Library', 'Application Support',
            'com.spitfireaudio.Spitfire_Audio_Library_Manager',
            'Spitfire_Audio_Library_Manager.storedata'
        ))
    except sqlite3.OperationalError:
        print(f'{RED}Error: Unable to open the Spitfire SQLite database{ENDC}')
        exit(1)

    # Build the main SQL to obtain library details
    sql = ('''
        SELECT l.zdisplaygroup AS 'Library Group',
               l.ztitle AS Library,
               lf.zfilename AS Filename,
               lf.zchecksum AS MD5,
               l.zinstallationfolder AS Folder,
               lf.zinstallationpath AS Path
        FROM zlibraryfile AS lf
        JOIN zlibrary AS l ON l.z_pk = lf.zlibrary
    ''')
    args = []

    # Filter the SQL by the search term if provided
    if search:
        sql += " WHERE l.zdisplaygroup LIKE ?"
        args.append(f'%{search}%')

    cursor = conn.execute(sql, args)
    spitfire_files = defaultdict(set)

    while True:
        # Grab the current row
        row = cursor.fetchone()
        if row is None:
            break

        # Unpack the row
        group, library, filename, md5, folder, path = row

        # Save the record into our data structure
        key = group if md5sums else f'{group} : {library}'

        spitfire_files[key].add((filename, md5, folder, path))

    # Print MD5 checksums of all items grouped by library
    if md5sums:
        for library, files in sorted(spitfire_files.iteritems()):
            for filename, md5, folder, path in sorted(files, key=lambda x: x[0]):
                if path:
                    filepath = os.path.join(folder, path, filename)
                else:
                    filepath = os.path.join(folder, filename)

                print(f'{md5}  {filepath}')

    # Print library information
    else:
        for library, files in sorted(spitfire_files.iteritems()):
            print()
            print(f'{YELLOW}{library}{ENDC}')
            print()
            for filename, md5, folder, path in sorted(files, key=lambda x: x[0]):
                if path:
                    filepath = os.path.join(folder, path, filename)
                else:
                    filepath = os.path.join(folder, filename)

                print(f'{BLUE}{md5}{ENDC}  {GREEN}{filepath}{ENDC}')
        print()


if __name__ == '__main__':
    main()
