#!/usr/bin/python
import web
import yapc.core as yapc
import yapc.log.output as output
import yapc.comm.openflow as ofcomm
import yapc.events.openflow as ofevents
import yapc.netstate.swhost as switchhost
import yapc.netstate.switches as swstate
import yapc.forwarding.switching as fswitch
import yapc.forwarding.default as default
import yapc.util.memcacheutil as mcutil
import yapc.debug.openflow as ofdbg
import yapc.log.sqlite as sqlite
import yapc.log.openflow as oflog

import openwifi.webpage as owweb
import openwifi.globals as owglobal
import openwifi.authenticate as owauth
import openwifi.logger as owlog
import sys
import time

output.set_mode("DBG")
mcutil.memcache_mode = mcutil.MEMCACHE_MODE["LOCAL"]
web.config.debug=False

server = yapc.core()
webcleanup = owweb.cleanup(server)
owglobal.server = server
ofconn = ofcomm.ofserver(server)
ofparse = ofevents.parser(server)
swconfig = swstate.dp_config(server, ofconn.connections)
swconfig.default_miss_send_len = 65535
swhost = switchhost.mac2sw_binding(server)
owredirect = owauth.redirect(server, ofconn.connections)
fsw = fswitch.learningswitch(server, ofconn.connections, True)
fp = default.floodpkt(server, ofconn.connections)
#pfr = ofdbg.show_flow_removed(server)
db = sqlite.SqliteDB(server, "openwifi.sqlite")
fl = oflog.flowlogger(server, db)
al = owlog.authlogger(server, db)
db.start()

webapp = web.application(owweb.urls, globals())
session = web.session.Session(webapp, 
                              web.session.DiskStore('sessions'), 
                              initializer={'datapath': None, 
                                           'host': None})
owglobal.session = session
hauth = owauth.host_auth(server)

if __name__ == "__main__": 
    server.run(runbg=True)
    webapp.run()
