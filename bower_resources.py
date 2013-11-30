#!/usr/bin/env python
# -*- coding: utf-8 -*-
from chut import rm
from chut import test
from chut import path
from chut import find
from chut import bower
from chut import console_script
from glob import glob
import json

dependencies = []
packages = {}


def extract_packages(package):
    dependencies.extend(
        package['pkgMeta'].get('dependencies', {}).keys())
    dirname = package['canonicalDir']
    files = package['pkgMeta']['main']
    if not isinstance(files, list):
        files = [files]
    assets = []
    for filename in files:
        filename = path.abspath(path(dirname, filename))
        assets.extend(glob(str(filename)))
    package['assets'] = assets
    for pkg in package['dependencies'].values():
        packages.update(package.get('dependencies', {}))
        extract_packages(pkg)


@console_script
def bower_resources(args):
    """Usage: %prog [--clean]
    """
    with open('.bowerrc') as fd:
        components = path.abspath(json.load(fd)['directory'])
    static = path.dirname(path.dirname(components))
    package = json.loads(str(bower('list --json --quiet')))
    extract_packages(package)
    resources = []
    done = []
    for name in reversed(dependencies):
        if name.lower() in done:
            continue
        done.append(name.lower())
        resources.extend(packages[name]['assets'])
    resources.extend(package['assets'])

    minifieds = []
    for i, resource in enumerate(resources):
        filename, ext = path.splitext(resource)
        minified = '.'.join([filename, 'min', ext.lstrip('.')])
        if test.f(minified):
            resource = minified
        minifieds.append(resource)

    for resource in minifieds:
        if resource.endswith('.css'):
            resource = resource[len(static):]
            print('<link rel="stylesheet" href="%s" />' % resource)

    print('')

    for resource in minifieds:
        if resource.endswith('.js'):
            resource = resource[len(static):]
            print('<script type="text/javascript" src="%s" />' % resource)

    print('')

    resources.extend(minifieds)

    if args['--clean']:
        for filename in find(components):
            if filename not in resources:
                if not filename.endswith('bower.json'):
                    if not test.d(filename):
                        print(filename)
                        rm('-f', filename)
        for filename in find(components, '-type d -empty'):
            rm('-r', filename)

if __name__ == '__main__':
    bower_resources()
