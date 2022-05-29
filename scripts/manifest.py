#!/bin/python3

# Generate a mainfest.yml file for the main directory in a git repository

# Note: This script is intended to be run from the root of the repository
#       and will be run automatically by the CI server
#	   (see .github/workflows/mainfest.yml)

# Only supports Linux (for now)

import sys
import os
import yaml
import datetime

yaml.Dumper.ignore_aliases = lambda *args: True

# Get specific flag passed to script


def get_flag(flag):
    for i in range(1, len(sys.argv)):
        if sys.argv[i] == flag:
            return sys.argv[i+1]
    return None


commit = get_flag('--commit')
repo = get_flag('--repo')

# Get list of dirs in a subdir that changed in the last commit


def get_changed_dirs(subdir):
    changed_dirs = []
    for line in os.popen('git show --name-only --pretty=format:"" --diff-filter=ACMRTUXB ' + commit).readlines():
        if line.startswith(subdir):

            # Check if line is a file or a directory
            if os.path.isfile(line.strip()):
                changed_dirs.append(os.path.dirname(line))

    # Remove duplicates and return

    return list(set(changed_dirs))


dirs = get_changed_dirs('manifest')

# Read manifest.yml
try:
    with open('manifest.yml', 'r') as m:
        mf_file = m.read()
except FileNotFoundError:
    mf_file = ''


# Get yaml data from mf_file
mf_yaml = yaml.load(mf_file, Loader=yaml.FullLoader)

print(mf_yaml)

# Check if mf_yaml is a empty dict
if not mf_yaml:
    print('manifest.yml is empty.')
    mf_yaml = {}

# Get name of repo
mf_yaml['name'] = repo
mf_yaml['latest_commit'] = commit
mf_yaml['last_updated'] = str(datetime.datetime.now())
mf_yaml['packages'] = {} if 'packages' not in mf_yaml else mf_yaml['packages']

# Check if dirs is empty
if len(dirs) == 0:
    print('No directories changed in manifest directory.')

# Remove empty dirs
dirs = [d for d in dirs if d != '']

print(dirs)

# Get list of files in each folder
for dir in dirs:
    print(dir)
    mf = {}
    mf['commit'] = commit
    mf['contents'] = []

    files = os.listdir(dir)
    for file in files:
        # Get file name with extension
        if (dir + "/" + file).endswith(".yml"):

            # Read from f.yml in dir
            with open(f'{dir + "/" + file}', 'r') as f:
                f_file = f.read()
                f_yaml = yaml.load(f_file, Loader=yaml.FullLoader)

                try:
                    ver = f_yaml['ver']
                except KeyError:
                    print('Invalid yaml file: ' + file)

        f_dict = {}
        f_dict['name'] = file
        f_dict['path'] = dir + "/" + file

        # Get sha256sum of file in dir
        os.system(f"sha256sum {f_dict['path']} > {f_dict['path']}.sha256sum")
        with open(f"{f_dict['path']}.sha256sum", 'r') as f:
            f_dict['sha256'] = f.read().split()[0]
        os.remove(f"{f_dict['path']}.sha256sum")

        # Get url of file in dir
        f_dict['url'] = f"https://raw.githubusercontent.com/{repo}/{commit}/{f_dict['path']}"

        mf['contents'].append(f_dict)

    pkg = dir.replace('manifests/', '')

    mf_yaml['packages'][pkg] = {} if mf_yaml['packages'].get(
        pkg) is None else mf_yaml['packages'][pkg]
    mf_yaml['packages'][pkg][ver] = [] if mf_yaml['packages'][pkg].get(
        ver) is None else mf_yaml['packages'][pkg][ver]

    if mf in mf_yaml['packages'][pkg][ver]:
        print(f"Modified {pkg} - {ver} already exists in manifest.yml")
    else:
        mf_yaml['packages'][pkg][ver].append(mf)

    print(mf)

# Write to manifest.yml
with open('manifest.yml', 'w+') as m:
    m.write('# Generated by Github Actions - DO NOT MODIFY NOR DELETE\n')
    m.write(yaml.dump(mf_yaml, default_flow_style=False, sort_keys=False))
