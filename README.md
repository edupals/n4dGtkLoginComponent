# n4dGtkLogincomponent
This is a Lliurex specific login component for Gtk apps.  
### API  
###### set_allowed_groups(groups=[])
	Login only will be succesfull if user belongs to any of this groups.
###### set_mw_proportion_ratio(columns_left,columns_right)  
	Sets the portion of screen reserved to each component (info and login form). It works splitting the main window in (columns_left+columns_right) columns and asigning to each part the desired number of columns. By default the proportion is set to 2:1
###### set_mw_background(image=None,cover=False,from_color=None,to_color=None,gradient='linear')  
	Sets the background for the login box. It can be a system's image or gradient going "from_color" to "to_color". By default all fields are "None" and only radial and linear gradients are supported. If we set a background image and set cover=True then the image will cover all the box area.
###### set_login_background(image=None,cover=False,from_color=None,to_color=None,gradient='linear')  
	Sets the background for the login box. It can be a system's image or gradient going "from_color" to "to_color". By default all fields are "None" and only radial and linear gradients are supported. If we set a background image and set cover=True then the image will cover all the box area.
###### set_default_username(default_username)  
	Sets the placeholder of the "username" entry to "default_username"  
###### set_default_server(default_server)  
	Sets the placeholder of the "server" entry to "default_server"  
###### set_login_banner(image)  
	Sets the user's image for the login form, by default is "llx-avatar" 
	If the image isn't a full path then is searched in the default theme.  
###### set_info_banner(image,resx=72,resy=72)  
	Sets the info box banner, by default is "None". The resolution is set to 72X72 by default.
###### set_info_background(image=None,cover=False,from_color=None,to_color=None,gradient='linear')  
	Sets the background for the info box. It can be a system's image or gradient going "from_color" to "to_color". By default all fields are "None" and only radial and linear gradients are supported. If we set a background image and set cover=True then the image will cover all the box area.
###### set_info_text(title,subtitle,text)  
	Sets the information to show in the info box.  
	It must have a title, a subtitle and a text as arguments and supports markup language.
###### hide_server_entry()  
	Hides the entry field of the login form
###### hide_info_box()  
	Hides the info box form
###### get_action_area()  
	Returns the info box so we can add any widget to it.  
###### after_validation_goto()  
	Sets the function that the loginComponent will launch after a correct user's validation. User, password and server will be passed as arguments to that function.
  
### Examples  
```python  
#!/usr/bin/env python3  
import gi  
gi.require_version('Gtk', '3.0')  
from gi.repository import Gtk  
from edupals.ui.n4dgtklogin import *  
  
def _signin():  
	print("OK")  
	print("Now hide the login component and make things")  
  
def start_gui():  
	mw=Gtk.Window()  
	loginComponent=N4dGtkLogin() #Init the login component  
	loginComponent.set_info_text("<span foreground='black'>Title</span>","Subtitle","Text text text.\nText text text:\n<sub>* text with sub tag</sub>")  
	#Uncomment and comment...
	##Change the proportion ratio 
	#loginComponent.set_mw_proportion_ratio(2,1)
	#loginComponent.set_mw_proportion_ratio(1,2)
	#loginComponent.set_mw_proportion_ratio(3,9)
	#loginComponent.set_mw_proportion_ratio(8,5)
	##- Setting a background for the component
	#loginComponent.set_mw_background(image='/usr/share/backgrounds/ubuntu-mate-xenial/The_MATErix.png')  
	##- Setting a background for the form
	#loginComponent.set_form_background(from_color='grey',to_color='white',gradient='radial')  
	##- Adding a widget to the info box
	#infobox=loginComponent.get_action_area()  
	#infobox.add(Gtk.Label("Add widget"))  
	##- Changing the background for the info box
	#loginComponent.set_info_background(from_color='#000000',to_color='white',gradient='linear')  
	#loginComponent.set_info_background(image='/usr/share/backgrounds/ubuntu-mate-xenial/The_MATErix.png')  
	##- Changing default values for entries
	#loginComponent.set_default_username("Put your name")  
	#loginComponent.set_default_server("Put your server")  
	##- Changing banners
	#loginComponent.set_login_banner('/usr/share/filezilla/resources/flatzilla/48x48/uploadadd.png')  
	#loginComponent.set_info_banner('/usr/share/filezilla/resources/flatzilla/24x24/folder.png')  
	##- Function that will be launched after a succesfull validation
	loginComponent.after_validation_goto(_signin)  
	##
	mw.add(loginComponent)
	mw.connect("delete-event",Gtk.main_quit)  
	mw.show_all()  
  
start_gui()  
Gtk.main()  
```
