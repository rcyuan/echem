import sys
import serial
import argparse

class Mux:
	def __init__(self, port = 'com3', debug = False, read_timeout = 1.0, write_timeout = 1.0):
		# Initialize Mux object & attempt to open specified serial port
		self.debug = debug
		try:
			self.comm = serial.Serial(port, 115200, timeout = read_timeout, write_timeout = write_timeout)
			if self.debug:
				sys.stderr.write(f'Connected to {port}.\n')
			if self.comm is None or not self.comm.is_open:
				sys.stderr.write('ERROR: \n')
		except serial.SerialException as e:
			sys.stderr.write(f'ERROR: Failed to open serial port {port}: {e}\n')
			self.comm = None

	def __del__(self):
		# Close serial connection if it was opened
		try:
			if hasattr(self, 'comm') and self.comm is not None:
				self.comm.close()
		except Exception as e:
			sys.stderr.write(f'ERROR: Exception in __del__: {e}\n')

	def send(self, cmd):
		# Send a command to mux; return reply as list of strings
		if self.comm is None:
			raise RuntimeError('ERROR: Serial port not initialized; cannot send command.')
		if self.debug:
			sys.stderr.write(f'>>> {cmd.strip()}\n')
			sys.stderr.flush()
		self.comm.write(bytearray(cmd + '\r', 'utf-8'))
		reply = str(self.comm.read_until().strip())[2:-1]
		if self.debug:
			sys.stderr.write(f'<<< {reply}\n')
			sys.stderr.flush()
		return reply.split(' ')

	def all(self):
		self.send('a\r')

	def none(self):
		self.send('n\r')

	def set(self, id):
		self.send('s{}\r'.format(id))

	def reset(self, id):
		self.send('r{}\r'.format(id))

	def toggle(self, id):
		self.send('t{}\r'.format(id))

	def up(self):
		self.send('u\r')

	def down(self):
		self.send('d\r')

	def close(self):
		if self.comm:
			self.comm.close()
			self.comm = None


def main():
	###
	# Program Arguments
	###
	ap = argparse.ArgumentParser(description='Mux State Control Tool')
	og = ap.add_argument_group('Device')
	og.add_argument('--debug', action='store_true', help='enable communication debugging')
	og.add_argument('--mux', default='com3', help='connect to specified mux COM port')
	og.add_argument('--read-timeout', type=float, default=1.0, help='COM port read time-out seconds')
	og.add_argument('--write-timeout', type=float, default=1.0, help='COM port write time-out seconds')
	og = ap.add_argument_group('Actions')
	og.add_argument('--all', action='store_true', help='enable all')
	og.add_argument('--none', action='store_true', help='disable all')
	og.add_argument('--up', action='store_true', help='shift left')
	og.add_argument('--down', action='store_true', help='shift right')
	og.add_argument('--set', type=int, nargs='+', metavar='CH', help='enable channel')
	og.add_argument('--reset', type=int, nargs='+', metavar='CH', help='disable channel')
	og.add_argument('--toggle', type=int, nargs='+', metavar='CH', help='toggle channel')
	args = ap.parse_args()

	###
	# MUX Operations
	###
	mux = Mux(args.mux, args.debug, args.read_timeout, args.write_timeout)

	if mux.comm is None:
		sys.stderr.write('Could not connect to MUX hardware. Exiting.\n')
		sys.exit(1)
	if args.all:
		mux.all()
	if args.none:
		mux.none()
	if args.up:
		mux.up()
	if args.down:
		mux.down()
	if not args.set is None:
		for ch in args.set:
			mux.set(ch)
	if not args.reset is None:
		for ch in args.reset:
			mux.reset(ch)
	if not args.toggle is None:
		for ch in args.toggle:
			mux.toggle(ch)

	mux.close()

if __name__ == '__main__':
	main()
