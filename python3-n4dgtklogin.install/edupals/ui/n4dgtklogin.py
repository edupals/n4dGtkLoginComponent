#!/usr/bin/env python3
###
#This class returns a HBox whith a standarized login form
###
import os,sys
import threading
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('PangoCairo', '1.0')
import json
import cairo
#import commands
from gi.repository import Gtk, Gdk, GdkPixbuf, GObject, GLib, PangoCairo, Pango
try:
	import xmlrpc.client as n4d
except ImportError:
	raise ImportError("xmlrpc not available. Disabling server queries")
import ssl
import time
import gettext
import pam

gettext.textdomain('nezumi.ui.common')
_ = gettext.gettext
GObject.threads_init()

class N4dGtkLogin():
	def __init__(self):
		threading.Thread.__init__(self)
		self.sw_n4d=True
		if hasattr(sys,'last_value'):
		#If there's any error at this point it only could be an ImportError caused by xmlrpc
			self.sw_n4d=False
		self.default_spacing=12
		self.username_placeholder=_("Username")
		self.server_placeholder=_("Server IP (Default value : server)")
		self.banner_default="llx-avatar"
		self.info_msg=''
		self.info_background=''
		self.mw_background=''
		self.form_background=''
		self.info_box=Gtk.Box(spacing=self.default_spacing,orientation=Gtk.Orientation.VERTICAL)
		self.txt_username=Gtk.Entry()
		self.txt_server=Gtk.Entry()
		self.banner=Gtk.Image()
		self.set_banner(self.banner_default)
		self.info_banner=None
		self.sw_info=False
		self.left_span=2
		self.right_span=1
	#def __init__

	def set_mw_proportion_ratio(self,left_span,right_span):
		self.left_span=left_span
		self.right_span=right_span
	
	def set_mw_background(self,image=None,from_color='#ffffff',to_color='silver',gradient='linear'):
		if image and os.path.isfile(image):
			self.mw_background='background-image:url("'+image+'"); background-repeat:no-repeat; background-size:cover'
		else:
			if gradient=='linear':
				self.mw_background='background-image:-gtk-gradient (linear, left top, left bottom, from ('+from_color+'),  to ('+to_color+'))'
			elif gradient=='radial':
				self.mw_background='background-image:-gtk-gradient (radial, center center,0,center center,1, from ('+from_color+'),  to ('+to_color+'))'
	#def set_mw_background

	def set_login_background(self,image=None,from_color='#ffffff',to_color='@silver',gradient='linear'):
		if image and os.path.isfile(image):
				self.form_background='background-image:url("'+image+'"); background-repeat:no-repeat; background-size:cover'
		else:
			if gradient=='linear':
				self.form_background='background-image:-gtk-gradient (linear, left top, left bottom, from ('+from_color+'),  to ('+to_color+'))'
			elif gradient=='radial':
				self.form_background='background-image:-gtk-gradient (radial, center center,0,center center,1, from ('+from_color+'),  to ('+to_color+'))'
	#def set_login_background

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
	
	def set_info_background(self,image=None,from_color='#ffffff',to_color='@silver',gradient='linear'):
		if image and os.path.isfile(image):
				self.info_background='background-image:url("'+image+'"); background-repeat:no-repeat;background-size:cover'
		else:
			if gradient=='linear':
				self.info_background='background-image:-gtk-gradient (linear, left top, left bottom, from ('+from_color+'),  to ('+to_color+'))'
			elif gradient=='radial':
				self.info_background='background-image:-gtk-gradient (radial, center center,0,center center,1, from ('+from_color+'),  to ('+to_color+'))'
	#def set_info_background

	def set_info_text(self,title,subtitle,text):
		sw_ok=True
		try:
			msg="<b><big>"+title+"</big></b>"
			self.info_msg=msg+'\n'+subtitle+'\n\n'+text
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
		mw_box=Gtk.Box(spacing=0,orientation=Gtk.Orientation.HORIZONTAL)
		(mw_bg,main_bg)=('','')

		main_box=Gtk.Grid()
		main_box.set_hexpand(True)
		main_box.set_vexpand(True)
		main_box.set_column_homogeneous(True)
		main_box.set_row_homogeneous(True)
		form_box=self._render_login_form(show_server)
		if self.sw_info:
			info_box=self._render_info_form()
			main_box.attach(info_box,1,1,self.left_span,1)
		main_box.attach(form_box,1+self.left_span,1,self.right_span,1)
		mw_box.pack_start(main_box,True,True,0)
		if self.mw_background:
			mw_bg='#mw {'+self.mw_background+';;}'
			mw_box.set_name("mw")
		if self.form_background:
			form_bg='#main {'+self.form_background+';;}'
			form_box.set_name("main")
		if mw_bg or form_bg:
			css=eval('b"""'+mw_bg+form_bg+'"""')
			style_provider=Gtk.CssProvider()
			style_provider.load_from_data(css)
			Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(),style_provider,Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
		return (mw_box)
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
		self.btn_sign=Gtk.Button(stock=Gtk.STOCK_OK)
		self.btn_sign.connect('clicked',self._validate)
		self.frame=Gtk.Frame()
		
		self.frame.set_shadow_type(Gtk.ShadowType.OUT)   
		hbox=Gtk.Grid()
		hbox.set_margin_left(self.default_spacing)
		hbox.set_margin_right(self.default_spacing)
		hbox.set_margin_top(self.default_spacing)
		hbox.set_margin_bottom(self.default_spacing)
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
		self.btn_sign.set_margin_top(self.default_spacing)
		hbox.attach(self.btn_sign,0,4,1,1)
#		self.frame.add(hbox)
		self.sta_info=Gtk.InfoBar()
		self.sta_info.set_show_close_button(True)
		self.sta_info.set_message_type(Gtk.MessageType.ERROR)
		self.lbl_error=Gtk.Label(_("Login failed"))
		self.sta_info.get_action_area().add(self.lbl_error)
		self.sta_info.set_visible(False)
		self.sta_info.set_no_show_all(True)
		self.sta_info.connect('response',self._info_hide)
		self.sta_info.set_valign(True)
		hbox.props.valign=Gtk.Align.CENTER
		hbox.props.halign=Gtk.Align.CENTER
		form_box.pack_start(self.sta_info,False,True,0)
		form_box.pack_start(hbox,True,True,0)
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
			self.info_box.pack_start(lbl_msg,True,True,0)
		css=eval('b"""#info {'+self.info_background+';;}"""')
		style_provider=Gtk.CssProvider()
		style_provider.load_from_data(css)
		Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(),style_provider,Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
		self.info_box.set_name("info")
		lbl_msg.props.valign=Gtk.Align.CENTER
		lbl_msg.props.halign=Gtk.Align.CENTER
		return(self.info_box)
	#def _render_info_form

	def _set_widget_default_props(self,widget,tooltip=None):
		widget.set_valign(True)
		widget.set_halign(True)
		widget.set_tooltip_text(tooltip)
	#def _set_widget_default_props

	def _info_hide(self,widget,data):
		self.sta_info.hide()
		self.frame.set_sensitive(True)
	#def _info_hide

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
	#def _validate

	def _t_validate(self,user,pwd,server):
		ret=[False]
		if self.sw_n4d:
			self.n4dclient=self._n4d_connect(server)
			try:
				loginMethod='N4d'
				ret=self.n4dclient.validate_user(user,pwd)
			except Exception as e:
				ret=[False,str(e)]
		else:
			loginMethod='PAM'
			p=pam.pam()
			if p.authenticate(user,pwd):
				ret=[True]

		self.spinner.stop()
		if not ret[0]:
			self.lbl_error.show()
			self.sta_info.show()
		if ret[0]:
			self.after_validate(loginMethod,user,pwd)
		#local validation
	#def _t_validate

	def after_validation_goto(self,func,data=None):
		self.after_validate=func
	#def after_validation_func

	def _n4d_connect(self,server):
		context=ssl._create_unverified_context()
		c = n4d.ServerProxy("https://"+server+":9779",context=context,allow_none=True)
		return c
