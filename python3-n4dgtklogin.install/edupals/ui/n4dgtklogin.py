#!/usr/bin/env python3
###
#This class returns a login_grid whith a standarized login form
###
import os,sys,socket
import threading
import netifaces 
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

gettext.textdomain('edupals.ui.common')
_ = gettext.gettext
GObject.threads_init()

class N4dGtkLogin(Gtk.Box):
	__gtype_name__='n4dgtklogin'

	def __init__(self,*args,**kwds):
		super().__init__(*args,**kwds)
		self.dbg=True
		self.vertical=False
		if 'orientation' in kwds.keys():
			if kwds['orientation']==Gtk.Orientation.VERTICAL:
				self.vertical=True
		self.sw_n4d=True
		if hasattr(sys,'last_value'):
		#If there's any error at this point it only could be an ImportError caused by xmlrpc
			self.sw_n4d=False
		self.css_classes={'#GtkEntry':'{font-family: Roboto;border:0px;border-bottom:1px grey solid;margin-top:0px;padding-top:0px;}'}
		self.style_provider=Gtk.CssProvider()
		Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(),self.style_provider,Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
		self.default_spacing=12
		self.username_placeholder=_("Username")
		self.server_placeholder=_("Server IP (Default value : server)")
		self.login_banner_default="llx-avatar"
		self.info_banner=None
		self.allowed_groups=[]
		#internal boxes
		self.form_box=Gtk.Box(spacing=0,orientation=Gtk.Orientation.VERTICAL)
		self.info_box=Gtk.Box(spacing=self.default_spacing,orientation=Gtk.Orientation.VERTICAL)
		self.main_grid=Gtk.Grid()
		self.render_form()
	#def __init__

	def _debug(self,msg):
		if self.dbg:
			print("%s",msg)

	def set_allowed_groups(self,groups):
		self.allowed_groups=groups
	#def set_allowed_groups

	def set_mw_proportion_ratio(self,left_panel,right_panel):
		for child in self.main_grid.get_children():
			self.main_grid.remove(child)
		if self.vertical:
#			self.main_grid.attach(self.info_box,0,0,1,left_panel)
#			self.main_grid.attach(self.form_box,0,0+left_panel,1,right_panel)
			self.main_grid.attach(self.form_box,0,0,1,left_panel)
			self.main_grid.attach(self.info_box,0,0+left_panel,1,right_panel)
			self.main_grid.set_margin_bottom(12)
		else:
			self.main_grid.attach(self.info_box,0,0,left_panel,1)
			self.main_grid.attach(self.form_box,0+left_panel,0,right_panel,1)
	#def set_mw_proportion_ratio
	
	def set_mw_background(self,image=None,cover=False,from_color='#ffffff',to_color='silver',gradient='linear'):
		mw_background=self._set_background(image,cover,from_color,to_color,gradient)
		self.css_classes['#mw']='{'+mw_background+';;}'
		self._set_css()
	#def set_mw_background

	def set_login_background(self,image=None,cover=False,from_color='#ffffff',to_color='@silver',gradient='linear'):
		form_background=self._set_background(image,cover,from_color,to_color,gradient)
		self.css_classes['#main']='{'+form_background+';;}'
		self._set_css()
	#def set_login_background

	def set_info_background(self,image=None,cover=False,from_color='#ffffff',to_color='@silver',gradient='linear'):
		info_background=self._set_background(image,cover,from_color,to_color,gradient)
		self.css_classes['#info']='{'+info_background+';;}'
		self._set_css()
	#def set_info_background

	def _set_css(self):
		css=''
		for css_class,style in self.css_classes.items():
			css=css+css_class+' '+style
		css_style=eval('b"""'+css+'"""')
		self.style_provider.load_from_data(css_style)
	#def _set_css

	def _set_background(self,image=None,cover=False,from_color='#ffffff',to_color='silver',gradient='linear'):
		bg=''
		if image and os.path.isfile(image):
			if cover:
				bg='background-image:url("'+image+'"); background-repeat:no-repeat; background-size:100% 100%'
			else:
				bg='background-image:url("'+image+'"); background-repeat:no-repeat;'
		elif image:
			self._debug("%s not found. Searching..."%image)
			#try to locate the image in the default theme
			icon_theme=Gtk.IconTheme.get_default()
			icon_sizes=icon_theme.get_icon_sizes(image)
			if icon_sizes:
				max_size=max(icon_sizes)
				icon=icon_theme.lookup_icon(image,max_size,0)
				icon_path=icon.get_filename()
				bg='background-image:url("'+icon_path+'"); background-repeat:no-repeat; background-size:100% 100%'

		else:
			if gradient=='linear':
				bg='background-image:-gtk-gradient (linear, left top, left bottom, from ('+from_color+'),  to ('+to_color+'))'
			elif gradient=='radial':
				bg='background-image:-gtk-gradient (radial, center center,0,center center,1, from ('+from_color+'),  to ('+to_color+'))'
		return bg
	#def _set_background

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

	def _lookup_user_face(self):
		sw_ok=False
		if os.path.isfile(os.path.expanduser('~/.face')):
			sw_ok=True
			self.set_login_banner(os.path.expanduser('~/.face'))
		return sw_ok
	#def _lookup_user_face

	def set_login_banner(self,image=None):
		avatar=None
		if image:
			avatar=self._get_image(image)
			if avatar==None:
				avatar=self._get_image("avatar-default")
			self.login_banner.set_from_pixbuf(avatar)
	#def set_banner

	def set_info_banner(self,banner,x=72,y=72):
		self.info_banner.set_from_pixbuf(self._get_image(banner))
	#def set_info_banner

	def _get_image(self,image,x=72,y=72):
		pixbuf=None
		icon_theme=Gtk.IconTheme.get_default()
		if icon_theme.has_icon(image):
			pixbuf=icon_theme.load_icon(image,x,0)
		else:
			if os.path.isfile(image):
				pixbuf=GdkPixbuf.Pixbuf.new_from_file_at_scale(image,x,y,True)
		return pixbuf
	#def _get_image
	
	def set_info_text(self,title,subtitle,text):
		sw_ok=True
		info_msg=''
		self.lbl_info_msg.set_width_chars(25)
		self.lbl_info_msg.set_max_width_chars(25)
		try:
			msg="<b><big>"+title+"</big></b>"
			info_msg=msg+'\n'+subtitle+'\n'+text
		except Exception as e:
			sw_ok=False
			print(e)
		self.lbl_info_msg.set_markup(info_msg)
		self.lbl_info_msg.show()
		return sw_ok
	#def set_info_text

	def hide_server_entry(self):
		self.txt_server.props.no_show_all=True
		self.txt_server.hide()
	#def hide_server_entry

	def hide_info_box(self):
		self.info_box.props.no_show_all=True
		self.info_box.hide()
	#def hide_info_box

	def get_action_area(self):
		return self.info_box
	#def get_action_area

	def render_form(self):
		self.main_grid.set_hexpand(True)
		self.main_grid.set_vexpand(True)
		self.main_grid.set_column_homogeneous(True)
		self.main_grid.set_row_homogeneous(True)
		self._render_login_form()
		self._render_info_form()
		if self.vertical:
			self.main_grid.attach(self.form_box,1,1,1,1)
			self.main_grid.attach(self.info_box,1,3,1,1)
			self.main_grid.set_margin_bottom(12)
		else:
			self.main_grid.attach(self.info_box,1,1,2,1)
			self.main_grid.attach(self.form_box,3,1,1,1)
		self.pack_start(self.main_grid,True,True,0)
		self.set_name("mw")
		self.form_box.set_name("main")
	#def render_form

	def _render_login_form(self):
		self.txt_username=Gtk.Entry()
		self.txt_username.set_name("GtkEntry")
		self.login_banner=Gtk.Image()
		if not self._lookup_user_face():
			self.set_login_banner(self.login_banner_default)
		self.login_banner.set_margin_bottom(self.default_spacing)
		self.set_default_username(self.username_placeholder)
		self.txt_username.set_icon_from_icon_name(Gtk.EntryIconPosition.PRIMARY,"system-users")
		self.txt_password=Gtk.Entry()
		self.txt_password.set_name("GtkEntry")
		self.txt_password.set_icon_from_icon_name(Gtk.EntryIconPosition.PRIMARY,"changes-prevent")
		self._set_text_for_entry(self.txt_password,_("Password"))
		self.txt_server=Gtk.Entry()
		self.txt_server.set_name("GtkEntry")
		self.set_default_server(self.server_placeholder)
		self.txt_server.set_icon_from_icon_name(Gtk.EntryIconPosition.PRIMARY,"network-wired")
		self.btn_sign=Gtk.Button(stock=Gtk.STOCK_OK)
		self.btn_sign.connect('clicked',self._validate)
		self.btn_sign.set_halign(Gtk.Align.CENTER)
		self.frame=Gtk.Frame()
		
		self.frame.set_shadow_type(Gtk.ShadowType.OUT)   
		login_grid=Gtk.Grid()
		login_grid.set_column_spacing(6)
		login_grid.set_row_spacing(6)
		login_grid.set_margin_left(self.default_spacing)
		login_grid.set_margin_right(self.default_spacing)
		login_grid.set_margin_top(self.default_spacing)
		login_grid.set_margin_bottom(self.default_spacing)
		self.spinner=Gtk.Spinner()
		self.spinner.set_no_show_all(True)
		color=Gdk.Color(0,0,1)
#		self.spinner.modify_bg(Gtk.StateType.NORMAL,color)
		login_grid.attach(self.spinner,0,1,2,5)
		if self.vertical:
			position=Gtk.PositionType.RIGHT
		else:
			position=Gtk.PositionType.BOTTOM

		login_grid.attach(self.txt_username,0,1,1,1)
		self._set_widget_default_props(self.txt_username,_("Username"))
		self.txt_username.connect('activate',self._validate)
		login_grid.attach_next_to(self.txt_password,self.txt_username,position,1,1)
		self._set_widget_default_props(self.txt_password,_("Password"))
		self.txt_password.set_visibility(False)
		self.txt_password.props.caps_lock_warning=True
		self.txt_password.connect('activate',self._validate)
		self._set_widget_default_props(self.txt_server,_("Master Server IP"))
		if self.vertical:
			self.txt_server.set_halign(Gtk.Align.FILL)
			self.txt_server.set_hexpand(True)
			login_grid.attach_next_to(self.txt_server,self.txt_username,Gtk.PositionType.BOTTOM,2,1)
		else:
			login_grid.attach_next_to(self.txt_server,self.txt_password,Gtk.PositionType.BOTTOM,1,1)
		self.txt_server.connect('activate',self._validate)
		self.btn_sign.set_margin_top(self.default_spacing)
		login_grid.attach_next_to(self.btn_sign,self.txt_server,Gtk.PositionType.BOTTOM,3,1)
		login_grid.attach(self.login_banner,0,0,3,1)
		self.sta_info=Gtk.InfoBar()
		self.sta_info.set_show_close_button(True)
		self.sta_info.set_message_type(Gtk.MessageType.ERROR)
		self.lbl_error=Gtk.Label(_("Login failed"))
		self.sta_info.get_action_area().add(self.lbl_error)
		self.sta_info.set_visible(False)
		self.sta_info.set_no_show_all(True)
		self.sta_info.connect('response',self._status_info_hide)
		if self.vertical:
			login_grid.props.valign=Gtk.Align.END
			login_grid.set_margin_bottom(0)
			self.btn_sign.set_margin_bottom(0)
		else:
			login_grid.props.valign=Gtk.Align.CENTER
		login_grid.props.halign=Gtk.Align.CENTER
		self.form_box.pack_start(self.sta_info,False,True,0)
		self.form_box.pack_start(login_grid,True,True,0)
	#def _render_login_form

	def _render_info_form(self):
		self.info_box.set_homogeneous(False)
		self.info_banner=Gtk.Image()
		info_detail_box=Gtk.Box(spacing=self.default_spacing,orientation=Gtk.Orientation.VERTICAL)
		info_detail_box.pack_start(self.info_banner,False,False,0)
		self.lbl_info_msg=Gtk.Label()
		self.lbl_info_msg.set_use_markup(True)
		self.lbl_info_msg.set_line_wrap(True)
		info_detail_box.pack_start(self.lbl_info_msg,True,True,0)
		if not '#label' in self.css_classes.keys():
			self.css_classes['#label']='{background-color:rgba(200,200,200,0.8);;}'
		self.lbl_info_msg.set_name("label")
		self.lbl_info_msg.set_no_show_all(True)
		self.lbl_info_msg.hide()
		self.info_box.set_name("info")
		if self.vertical:
#			self.lbl_info_msg.props.halign=Gtk.Align.FILL
			self.lbl_info_msg.set_justify(Gtk.Justification.CENTER)
			self.lbl_info_msg.set_margin_left(12)
			self.lbl_info_msg.set_margin_right(12)
			info_detail_box.props.valign=Gtk.Align.START
		else:
			info_detail_box.props.valign=Gtk.Align.CENTER
			info_detail_box.props.halign=Gtk.Align.CENTER
		if self.vertical:
			self.info_box.pack_start(info_detail_box,False,False,0)
		else:
			self.info_box.pack_start(info_detail_box,True,True,0)
		self._set_css()
	#def _render_info_form

	def set_label_background(self,r,g,b,a):
		self.css_classes['#label']='{background-color:rgba(%s,%s,%s,%s);;}'%(r,g,b,a)

	def _set_widget_default_props(self,widget,tooltip=None):
		widget.set_valign(True)
		widget.set_halign(True)
		widget.set_tooltip_text(tooltip)
	#def _set_widget_default_props

	def _status_info_hide(self,widget,data):
		self.sta_info.hide()
		self.frame.set_sensitive(True)
	#def _info_hide

	def _validate(self,widget=None):
		user=self.txt_username.get_text()
		pwd=self.txt_password.get_text()
		server=self.txt_server.get_text()
		server_ip=''
		if not server:
			server='server'
		try:
			server_ip=socket.gethostbyname(server)
		except:
			server='localhost'
		#Check if localhost is server
		for iface in netifaces.interfaces():
			for key,netinfo in netifaces.ifaddresses(iface).items():
				for info in netinfo:
					if info['addr']==server_ip:
						server='localhost'
						break

		self.spinner.show()
		self.spinner.start()
		self.frame.set_sensitive(False)
		th=threading.Thread(target=self._t_validate,args=[user,pwd,server])
		th.start()
	#def _validate

	def _t_validate(self,user,pwd,server):
		ret=[False]
		self.lbl_error.set_text(_("Login failed"))
		if self.sw_n4d:
			try:
				self.n4dclient=self._n4d_connect(server)
				ret=self.n4dclient.validate_user(user,pwd)
			except socket.error as e:
				self.lbl_error.set_text(_("Unknown host"))
				ret=[False,str(e)]

		self.spinner.stop()
		self.spinner.hide()
		if not ret[0]:
			self.sta_info.show()
			self.lbl_error.show()
			#show server entry if we can't connect to n4d in "server"
			self.txt_server.props.no_show_all=False
			self.txt_server.show()
		elif self.allowed_groups and not set(self.allowed_groups).intersection(ret[1]):
			#Check user groups
			self.lbl_error.set_text(_("User not allowed"))
			self.sta_info.show()
			self.lbl_error.show()
		else:
			GLib.idle_add(self.after_validate,user,pwd,server)
		#local validation
	#def _t_validate

	def after_validation_goto(self,func,data=None):
		self.after_validate=func
	#def after_validation_func

	def _n4d_connect(self,server):
		context=ssl._create_unverified_context()
		try:
			socket.gethostbyname(server)
		except:
			#It could be an ip
			try:
				socket.inet_aton(server)
			except Exception as e:
				print(e)
				raise
		c = n4d.ServerProxy("https://"+server+":9779",context=context,allow_none=True)
		return c
	#def _n4d_connect
