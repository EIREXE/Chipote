# The free comic format
# Copyright (C) 2016  Alex Roman
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3 as
# published by the Free Software Foundation.
import os
import gi
import sys
import zipfile

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk
from gi.repository.GdkPixbuf import InterpType, PixbufLoader


class Handler:
    def on_window_close(self, widget, what):
        Gtk.main_quit()
    def on_draw(self, widget, cr):
        cr.set_source_rgb(0,0,0)
        cr.rectangle(64,32, 0, 0)
handler = Handler()
builder = Gtk.Builder()
builder.add_from_file("main.glade")
builder.connect_signals(handler)

window = builder.get_object("MainWindow")

window.show_all()

Gtk.main()