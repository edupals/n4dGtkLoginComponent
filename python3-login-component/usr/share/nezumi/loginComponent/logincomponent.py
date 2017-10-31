#!/usr/bin/env python3
###
#This class returns a HBox whith a standarized login form
###
import os
import threading
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('PangoCairo', '1.0')
import json
import cairo
#import commands
from gi.repository import Gtk, Gdk, GdkPixbuf, GObject, GLib, PangoCairo, Pango
import xmlrpc.client as n4d
import ssl
import time
import gettext

gettext.textdomain('nezumi.ui.common')
_ = gettext.gettext
GObject.threads_init()

class loginN4DComponent():
	def __init__(self):
		threading.Thread.__init__(self)
		self.sw_n4d=False
		self.username_placeholder="Username"
		self.server_placeholder="Server IP (Default value : server)"
		self.banner_default="llx-avatar"
		self.info_msg=''
		self.info_background=''
		self.info_box=Gtk.Box(spacing=6,orientation=Gtk.Orientation.VERTICAL)
		self.txt_username=Gtk.Entry()
		self.txt_server=Gtk.Entry()
		self.banner=Gtk.Image()
		self.set_banner(self.banner_default)
		self.info_banner=None
		self.sw_info=False
	#def __init__

	def set_default_username(self,username):
		self.username_placeholder=username
		self._set_text_for_entry(self.txt_username,username)
	#def set_default_username

	def set_default_server(self,server):
		self.server_placeholder=server
		if self.txt_server:
			self._set_text_for_entry(self.txt_server,server)
	#def set_default_server
	
	def _set_text_for_entry(self,widget,text):
		widget.set_placeholder_text(text)
	#def _set_text_for_entry
	
	def set_banner(self,banner):
		self.banner=self._get_image(banner)
	#def set_banner

	def set_info_banner(self,image):
		self.info_banner=self._get_image(image)
	#def set_info_banner

	def _get_image(self,image):
		icon_theme=Gtk.IconTheme.get_default()
		img=Gtk.Image()
		if icon_theme.has_icon(image):
			img.set_from_icon_name(image,Gtk.IconSize.DIALOG)
		else:
			if os.path.isfile(image):
				pixbuf=GdkPixbuf.Pixbuf.new_from_file_at_scale(image,-1,Gtk.IconSize.DIALOG,True)
				img.set_from_pixbuf(pixbuf)
		return img
	
	def set_info_background(self,image=None,from_color='#ffffff',to_color='@silver'):
		if image and os.path.isfile(image):
			self.info_background='background-image:url("'+image+'"); background-repeat:no-repeat'
		else:
			self.info_background='background-image:-gtk-gradient (linear, left top, left bottom, from ('+from_color+'),  to ('+to_color+'))'
	#def set_info_background

	def set_info_text(self,title,subtitle,text):
		sw_ok=True
		try:
			msg="<b><big>"+title.title()+"</big></b>"
			msg_sub=subtitle.upper()
			self.info_msg=msg+'\n'+msg_sub+'\n\n'+text
			self.sw_info=True
		except Exception as e:
			sw_ok=False
			print(e)
		return sw_ok
	#def set_info_text

	def get_action_area(self):
		self.sw_info=True
		return self.info_box

	def render_form(self,show_server=True):
		main_box=Gtk.Box(spacing=0,orientation=Gtk.Orientation.HORIZONTAL)
		main_box.props.halign=Gtk.Align.CENTER
		main_box.props.valign=Gtk.Align.CENTER
		form_box=self._render_login_form(show_server)
		if self.sw_info:
			info_box=self._render_info_form()
			main_box.pack_start(info_box,True,True,0)
		main_box.pack_start(form_box,True,True,0)
		return (main_box)
	#def render_form

	def _render_login_form(self,show_server):
		form_box=Gtk.Box(spacing=0,orientation=Gtk.Orientation.VERTICAL)
		self.set_default_username(self.username_placeholder)
		self.txt_username.set_icon_from_icon_name(Gtk.EntryIconPosition.PRIMARY,"emblem-personal")
		self.txt_password=Gtk.Entry()
		self.txt_password.set_icon_from_icon_name(Gtk.EntryIconPosition.PRIMARY,"badge-small")
		self._set_text_for_entry(self.txt_password,_("Password"))
		self.txt_server=Gtk.Entry()
		self.set_default_server(self.server_placeholder)
		self.txt_server.set_icon_from_icon_name(Gtk.EntryIconPosition.PRIMARY,"server")
#		self.banner=Gtk.Image()
#		self.set_banner(self.banner_default)
		self.btn_sign=Gtk.Button(label=_("Sign In"),stock=Gtk.STOCK_OK)
		self.btn_sign.connect('clicked',self._validate)
		self.frame=Gtk.Frame()
		
		self.frame.set_shadow_type(Gtk.ShadowType.OUT)   
		hbox=Gtk.Grid()
		hbox.set_margin_left(6)
		hbox.set_margin_right(6)
		hbox.set_margin_top(6)
		hbox.set_margin_bottom(6)
		self.spinner=Gtk.Spinner()
		color=Gdk.Color(0,0,1)
		self.spinner.modify_bg(Gtk.StateType.NORMAL,color)
		hbox.attach(self.spinner,0,1,1,5)
		hbox.attach(self.banner,0,0,1,1)
		hbox.attach(self.txt_username,0,1,1,1)
		self._set_widget_default_props(self.txt_username,_("Username"))
		self.txt_username.connect('activate',self._validate)
		hbox.attach(self.txt_password,0,2,1,1)
		self._set_widget_default_props(self.txt_password,_("Password"))
		self.txt_password.set_visibility(False)
		self.txt_password.props.caps_lock_warning=True
		self.txt_password.connect('activate',self._validate)
		if show_server:
			hbox.attach(self.txt_server,0,3,1,1)
			self._set_widget_default_props(self.txt_server,_("Master Server IP"))
			self.txt_server.connect('activate',self._validate)
		hbox.attach(self.btn_sign,0,4,1,1)
		self.frame.add(hbox)
		self.sta_info=Gtk.InfoBar()
		self.sta_info.set_show_close_button(True)
		self.sta_info.set_message_type(Gtk.MessageType.ERROR)
		self.lbl_error=Gtk.Label(_("Login failed"))
		self.sta_info.get_action_area().add(self.lbl_error)
		self.sta_info.set_visible(False)
		self.sta_info.set_no_show_all(True)
		self.sta_info.connect('response',self._info_hide)
		self.sta_info.set_valign(True)
		form_box.pack_start(self.sta_info,False,True,0)
		form_box.pack_start(self.frame,True,False,0)
		return(form_box)
	#def _render_login_form

	def _render_info_form(self):
		if self.info_banner:
			self.info_box.add(self.info_banner)
		if self.info_msg:
			lbl_msg=Gtk.Label()
			lbl_msg.set_use_markup(True)
			lbl_msg.set_line_wrap(True)
			lbl_msg.set_width_chars(25)
			lbl_msg.set_max_width_chars(25)
			lbl_msg.set_markup(self.info_msg)
			self.info_box.add(lbl_msg)
#		css=eval('b"""#info {background-image:'+self.info_background+';;}"""')
		css=eval('b"""#info {'+self.info_background+';;}"""')
		style_provider=Gtk.CssProvider()
		style_provider.load_from_data(css)
		Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(),style_provider,Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
		self.info_box.set_name("info")
		return(self.info_box)

	def _set_widget_default_props(self,widget,tooltip=None):
		widget.set_valign(True)
		widget.set_halign(True)
		widget.set_tooltip_text(tooltip)

	def _info_hide(self,widget,data):
		self.sta_info.hide()
		self.frame.set_sensitive(True)

	def _validate(self,widget=None):
		user=self.txt_username.get_text()
		pwd=self.txt_password.get_text()
		server=self.txt_server.get_text()
		if not server:
			server='server'
		self.spinner.start()
		self.frame.set_sensitive(False)
		th=threading.Thread(target=self._t_validate,args=[user,pwd,server])
		th.start()

	def _t_validate(self,user,pwd,server):
		sw_ok=True
		time.sleep(3)
		context=ssl._create_unverified_context()
		c = n4d.ServerProxy("https://"+server+":9779",context=context,allow_none=True)
		ret=None
		try:
		    ret=c.validate_user(user,pwd)
		except Exception as e:
			sw_ok=False
			ret=[False,str(e)]
		self.spinner.stop()
		if not ret[0]:
			self.lbl_error.show()
			self.sta_info.show()
		if ret[0]:
			self.after_validate()

	def after_validation_func(self,func,data=None):
		self.after_validate=func

	def _n4d_connect(self):
		return sw_n4d
