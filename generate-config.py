#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import os
import re
import pathlib
import configparser

from collections import OrderedDict

ABBS_TREE = '/mnt/data/aosc/TREE'

KEYWORDS = {
    'pypi.io': 'pypi',
    'github.com': 'github',
    'gitlab.com': 'gitlab',
    'bitbucket.org': 'bitbucket',
}

EXTRACTORS = dict()


def extract_pypi(source):
    try:
        name = re.search(r'\/[a-zA-Z0-9]\/[\.a-zA-Z0-9_-]*\/', source).group(0)
        return name[3:-1]
    except AttributeError as e:
        print('Failed to parse %s: %s' % (source, e))
        return None


EXTRACTORS['pypi'] = extract_pypi


def extract_github(source):
    source = source.replace('.git', '')\
        .replace('//github.com', '')\
        .replace('//gitlab.com', '')\
        .replace('//bitbucket.org', '') + '/'
    try:
        name = re.search(r'\/[a-zA-Z0-9-_]*\/[\.a-zA-Z0-9-_]*\/', source).group(0)
        return name[1:-1]
    except AttributeError as e:
        print('Failed to parse %s: %s' % (source, e))
        return None


EXTRACTORS['github'] = extract_github
EXTRACTORS['gitlab'] = extract_github
EXTRACTORS['bitbucket'] = extract_github


def find_spec(target):
    for path, subdirs, files in os.walk(target):
        for name in (files + subdirs):
            next_path = pathlib.PurePath(path, name)
            if next_path.name == 'spec':
                yield next_path

def parse_spec(spec_path):
    spec_info = dict()
    with open(spec_path) as spec_file:
        spec_content = spec_file.readlines()
    for line in spec_content:
        if line.startswith('VER='):
            spec_info['ver'] = line.replace('VER=', '')[:-1]
            continue
        elif line.startswith('SRCTBL="'):
            source = line.replace('SRCTBL="', '')[:-2]
            for keyword in KEYWORDS.keys():
                if keyword in source:
                    parameter = EXTRACTORS[KEYWORDS[keyword]](source)
                    if parameter is not None:
                        spec_info['type'] = KEYWORDS[keyword]
                        spec_info['parameter'] = parameter
                    else:
                        return None
        if 'type' not in spec_info.keys():
            return None
    return spec_info

def write_source(info):
    source = configparser.ConfigParser()
    source['__config__'] = {'oldver': 'old_ver.txt', 'newver': 'new_ver.txt', 'max_concurrent': '1'}
    for pkg in info.keys():
        source[pkg] = {info[pkg]['type']: info[pkg]['parameter'], 'use_max_tag': True}
    with open('source.ini', 'w') as source_file:
        source.write(source_file)

def write_vers(info):
    vers = ''
    for pkg in info.keys():
        vers += '%s %s\n' % (pkg, info[pkg]['ver'])
    with open('old_ver.txt', 'w') as vers_file:
        vers_file.write(vers)

def main():
    info = dict()
    specs = find_spec(ABBS_TREE)
    for spec_path in specs:
        pkg_info = parse_spec(spec_path)
        if pkg_info:
            info[spec_path.parent.name] = pkg_info
    info = OrderedDict(sorted(info.items()))
    write_source(info)
    write_vers(info)


if __name__ == '__main__':
    main()