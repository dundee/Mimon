import sys

config = {}
config['modules'] = []
config['data_dir'] = '/var/lib/mimon'
config['pid_file'] = '/var/run/mimon.pid'

def read(file):
	try:
		fp = open(file, "r")
		lines = fp.readlines()
		fp.close()
	except IOError, e:
		print 'Configuration file (%s) not found or not readable' % file
		sys.exit(1)

	for line in lines:
		parts = line.split('#')
		statement = parts[0].strip()
		while statement.find('  ') != -1:
			statement = statement.replace('  ', ' ')
		if statement == '':
			continue
		operands = statement.split(' ')
		key = operands.pop(0)

		if key == 'LoadModule':
			for operand in operands:
				config['modules'].append(operand)
		elif key == 'DataDir':
			config['data_dir'] = ' '.join(operands)
	return config

def main():
	#read('/etc/mimon.conf')
	read('mimon.conf')
	return 0

if __name__ == '__main__': main()
