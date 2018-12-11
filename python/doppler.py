#!/usr/bin/env python
'''
   Copyright 2015 Wolfgang Nagele

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
'''
from gnuradio import gr
import threading
import time
import socket
import thread


class doppler(gr.basic_block):
  def __init__(self, callback, gpredict_host, gpredict_port, verbose):

    gr.basic_block.__init__(self,
        name="doppler",
        in_sig=None,
        out_sig=None)

    self.callback = callback
    self.gpredict_host = gpredict_host
    self.gpredict_port = gpredict_port
    self.verbose = verbose

    thread.start_new_thread(self.loop, ())


  def loop(self):
    bind_to = (self.gpredict_host, self.gpredict_port)
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(bind_to)
    server.listen(0)

    time.sleep(0.5) # TODO: Find better way to know if init is all done

    while True:
      if self.verbose: print "Waiting for connection on: %s:%d" % bind_to
      sock, addr = server.accept()
      if self.verbose: print "Connected from: %s:%d" % (addr[0], addr[1])

      cur_freq = 0
      while True:
        data = sock.recv(1024)
        if not data:
          break

        try:
          if data.startswith('F'):
            freq = int(data[1:].strip())
            if cur_freq != freq:
              if self.verbose: print "New frequency: %d" % freq
              self.callback(freq)
              cur_freq = freq
            sock.sendall("RPRT 0\n")
          elif data.startswith('f'):
            sock.sendall("f: %d\n" % cur_freq)
        except Exception as e:
          print e

      sock.close()
      if self.verbose: print "Disconnected from: %s:%d" % (addr[0], addr[1])
