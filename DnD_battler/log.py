import logging, sys

log = logging.getLogger('DnD')
log.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.WARNING)
handler.set_name('stdout')
log.addHandler(handler)
