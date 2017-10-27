#!/usr/bin/env python3
###
#This class returns a HBox whith a standarized login form
###
import gi                                                                                                      
gi.require_version('Gtk', '3.0')
gi.require_version('PangoCairo', '1.0')
import json
import cairo
#import commands
from gi.repository import Gtk, Gdk, GdkPixbuf, GObject, GLib, PangoCairo, Pango
import xmlrpc.client as n4d
import ssl

import gettext

gettext.textdomain('nezumi.login-component')
_ = gettext.gettext

class loginComponent():
	def __init__(self):
		self.main_box=Gtk.Box(spacing=6)
		self.txt_username=Gtk.Entry()
		self.txt_password=Gtk.Entry()
		self.txt_server=Gtk.Entry()
		self.banner=Gtk.Image()
		self.set_default_username("Username")
		self._set_text_for_entry("Password",self.txt_password)
		self.set_default_server("Server IP    (Default value : server)")
		self.txt_username.set_icon_from_icon_name(Gtk.EntryIconPosition.PRIMARY,"emblem-personal")
		self.txt_password.set_icon_from_icon_name(Gtk.EntryIconPosition.PRIMARY,"badge-small")
		self.txt_server.set_icon_from_icon_name(Gtk.EntryIconPosition.PRIMARY,"server")
		self.btn_sign=Gtk.Button(label=_("Sign In"),stock=Gtk.STOCK_YES)
		self.btn_sign.connect('clicked',self._validate)

	def _set_text_for_entry(self,text,widget):
		widget.set_placeholder_text(text)

	def set_default_username(self,username):
		self._set_text_for_entry(username,self.txt_username)
	#def set_default_username

	def set_default_server(self,server):
		self._set_text_for_entry(server,self.txt_server)
	#def set_default_server
	
	def set_banner(self,banner):
		pass
	#def set_banner

	def render_form(self,show_server=True):
		frame=Gtk.Frame()
		frame.set_shadow_type(Gtk.ShadowType.OUT)   
		hbox=Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=6)
		hbox.add(self.banner)
		hbox.add(self.txt_username)
		hbox.add(self.txt_password)
		if show_server:
			hbox.add(self.txt_server)
		hbox.add(self.btn_sign)
		frame.add(hbox)
		self.main_box.add(frame)
		return (self.main_box)

		self.toolbar.hide()
		self.toolbar.hide()

	def _validate(self,widget=None):
		user=self.txt_username.get_text()
		pwd=self.txt_password.get_text()
		print("Validating user %s %s"%(user,pwd))
		server=self.txt_server.get_text()
		if not server:
			server='server'

		context=ssl._create_unverified_context()
		c = n4d.ServerProxy("https://"+server+":9779",context=context,allow_none=True)
		ret=None
		try:
		    ret=c.validate_user(user,pwd)
		except Exception as e:
			print("ERROR %s"%e)
			ret=[False,str(e)]
			return
		print("RET: %s"%ret)
		if ret[0]:
			self.after_validate()

	def accept_signal(self,func,data=None):
		self.after_validate=func
