import sys
import SocketServer
import socket
import threading
import time

import os
import hashlib
import random

from msg import Msg
from qrgen import GetRandomQR

HOST = '0.0.0.0'
PORT = None
ANSWER_TIMEOUT = 5

SOLUTIONS_TO_WIN = 50

class MainHandler( SocketServer.BaseRequestHandler ):

	def handle( self ):
		self.request.sendall( Msg.SERVER_BANNER )
		self.request.sendall( Msg.SERVER_RULES )
		self.request.sendall( Msg.SESSION_START )

		answer = self.request.recv( 1024 ).strip()

		if answer != 'Y':
			self.request.sendall( Msg.EXIT )
			self.request.close()
			return -1

		CountOfSolves = 0

		while 1:

			if CountOfSolves == SOLUTIONS_TO_WIN:
				self.request.sendall( Msg.SERVER_AWARD )
				self.request.sendall( Msg.EXIT )
				self.request.close()
				
				break

			round_image, round_image_answer = GetRandomQR()

			self.request.sendall( round_image )
			self.request.settimeout( ANSWER_TIMEOUT )
			self.request.sendall( Msg.ANSWER_MSG )

			user_image_answer = ''

			try:
				user_image_answer = self.request.recv( 1024 ).strip()
			except:
				self.request.sendall( Msg.SERVER_ANSWER_TIMEOUT )
				self.request.sendall( Msg.EXIT )
				self.request.close()

				break

			if user_image_answer == round_image_answer:
				CountOfSolves += 1
				self.request.sendall( Msg.CORRECT_QR )
			else:
				self.request.sendall( Msg.INCORRECT_QR )
				self.request.sendall( Msg.EXIT )
				self.request.close()

				break 

		self.request.close()

class ThreadedTCPServer( SocketServer.ThreadingMixIn, SocketServer.TCPServer ):
	pass


if __name__ == "__main__":

	if len( sys.argv ) > 1:
		PORT = int( sys.argv[ 1 ] )
	else:
		print "Usage: python " + sys.argv[ 0 ] + " <port>"
		sys.exit( -1 )

	server = ThreadedTCPServer( ( HOST, PORT ), MainHandler )

	ip, port = server.server_address

	server_thread = threading.Thread( target = server.serve_forever )
	server_thread.daemon = False
	server_thread.start()

	while True:
		try:
			time.sleep( 1 )
		except:
			break

	server.shutdown()
	server.server_close()
