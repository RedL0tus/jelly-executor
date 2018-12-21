#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import sys

from distutils.util import strtobool
from pyrogram import Client

PAKREQ_BOT = 434703826

def user_yes_no_query(question):
    sys.stdout.write('%s [y/n]' % question)
    while True:
        try:
            return strtobool(input().lower())
        except ValueError:
            sys.stdout.write('Please respond with \'y\' or \'n\'.\n')

def main():
    app = Client('Jelly-executor')
    with app:
        with open('new_ver.txt') as newver_file:
            new_vers = newver_file.readlines()
        with open('old_ver.txt') as oldver_file:
            old_vers = oldver_file.readlines()
        for line in new_vers:
            line_splitted = line.split(' ')
            name = line_splitted[0]
            new_ver = line_splitted[1][:-1]
            old_ver = ''.join(old for old in old_vers if name == old.split(' ')[0]).split(' ')[1][:-1]
            if new_ver != old_ver:
                if user_yes_no_query('%s: from %s to %s?' % (name, old_ver, new_ver)):
                    app.send_message(PAKREQ_BOT ,'/updreq %s %s' % (name, new_ver))


if __name__ == '__main__':
    main()