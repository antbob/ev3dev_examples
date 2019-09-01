#!/usr/bin/env python
# coding: utf-8
"""
  ----------------------------------------------------------------------------
  "THE BEER-WARE LICENSE" (Revision 42):
  <antbob@users.noreply.github.com> wrote this file. As long as you retain
  this notice you can do whatever you want with this stuff. If we meet
  some day, and you think this stuff is worth it, you can buy me a beer in
  return Anton Bobrov
  ----------------------------------------------------------------------------
"""

from pyev3.rubiks import Rubiks
import logging
import rpyc

RPYCPORT = 18861

logging.basicConfig(filename='rubiks.log',
  filemode='w', level=logging.INFO,
  format='%(asctime)s %(filename)12s %(levelname)8s: %(message)s')
log = logging.getLogger(__name__)

class QService(rpyc.Service):

  rub = None

  def on_connect(self, conn):
    log.info('connect...')
    self.rub = Rubiks()

  def on_disconnect(self, conn):
    try:
      self.rub.mot_push.wait_for_stop()
      self.rub.mot_bras.wait_for_stop()
      self.rub.mot_rotate.wait_for_stop()
      self.rub.mot_push.stop()
      self.rub.mot_bras.stop()
      self.rub.mot_rotate.stop()
    except Exception as e:
        self.rub.leds.set_all('red')
        log.exception(e)

  def exposed_scan_cube(self):
    try:
      self.rub.leds.set_all('green')
      self.rub.wait_for_cube_insert()
      cube_kociemba = self.rub.scan()
      return cube_kociemba
    except Exception as e:
      self.rub.leds.set_all('red')
      log.exception(e)

  def exposed_resolve_cube(self, actions):
    try:
      self.rub.run_kociemba_actions(actions)
      self.rub.cube_done()
      self.rub.leds.set_all('green')
    except Exception as e:
      self.rub.leds.set_all('red')
      log.exception(e)

if __name__ == "__main__":
    from rpyc.utils.server import ForkingServer
    server = ForkingServer(QService, port=RPYCPORT)
    server.start()
