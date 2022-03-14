#!/bin/python3

# Generate a mainfest.yml file for the main directory in a git repository

# Note: This script is intended to be run from the root of the repository
#       and will be run automatically by the CI server 
#	   (see .github/workflows/mainfest.yml)

# Only supports Linux (for now)

import sys
import os
import yaml

yaml.Dumper.ignore_aliases = lambda *args : True

# Get specific flag passed to script
def get_flag(flag):
	for i in range(1, len(sys.argv)):
		if sys.argv[i] == flag:
			return sys.argv[i+1]
	return None

commit = get_flag('--commit')
		

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

# Check if dirs is empty
if len(dirs) == 0:
	exit('No directories changed in manifest directory.')

# Remove empty dirs
dirs = [d for d in dirs if d != '']

print(dirs)

# Read manifest.yml
with open('manifest.yml', 'r') as m:
	mf_file = m.read()

# Get yaml data from mf_file
mf_yaml = yaml.load(mf_file, Loader=yaml.FullLoader)

print(mf_yaml)

# Check if mf_yaml is a empty dict
if not mf_yaml:
	print('manifest.yml is empty.')
	exit('todo: add support for creating manifest.')

mf_yaml['latest_commit'] = commit

# Get list of files in each folder
for dir in dirs:
	print(dir)
	mf = {}
	mf['commit'] = commit
	
	files = os.listdir(dir)
	for file in files:
		# Get file name with extension
		if (dir + "/" + file).endswith(".yml"):

			# Read from f.yml in dir
			with open(f'{dir + "/" + file}', 'r') as f:
				f_file = f.read()
				f_yaml = yaml.load(f_file, Loader=yaml.FullLoader)

				try:
					mf['ver'] = f_yaml['ver']
					mf['updates'] = f_yaml['updates']
				except KeyError: 
					print('Invalid yaml file: ' + file)

		mf[file] = {}
		mf[file]['path'] = dir + "/" + file
		
		# Get sha256sum of file in dir
		os.system(f"sha256sum {mf[file]['path']} > {mf[file]['path']}.sha256sum")
		with open(f"{mf[file]['path']}.sha256sum", 'r') as f:
			mf[file]['sha256'] = f.read().split()[0]
		os.remove(f"{mf[file]['path']}.sha256sum")

		# Get url of file in dir
		mf[file]['url'] = f"https://raw.githubusercontent.com/m1ten/neopkgs/{commit}/{mf[file]['path']}"

	# Add mf to mf_yaml
	dir = dir.replace('manifests/', '')
	try:
		if mf in mf_yaml[dir]:
			print(f"Modified {dir} already exists in manifest.yml")
		mf_yaml[dir].append(mf)
	except KeyError:
		mf_yaml[dir] = [mf]

	print(mf)

# Write to manifest.yml
with open('manifest.yml', 'w') as m:
	m.write(yaml.dump(mf_yaml, default_flow_style=False, sort_keys=False))