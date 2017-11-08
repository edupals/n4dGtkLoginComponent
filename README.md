# n4dGtkLogincomponent
This is a Lliurex specific login component for Gtk apps.  
### API  
###### set_default_username(default_username)  
	Sets the placeholder of the "username" entry to "default_username"  
###### set_default_server(default_server)  
	Sets the placeholder of the "server" entry to "default_server"  
###### set_banner(image)  
	Sets the user's image for the login form, by default is "llx-avatar"  
	If the image isn't a full path then is searched in the default theme.  
###### set_info_banner(image)  
	Sets the info box banner, by default is "None"  
###### set_info_background(image=None,from_color=None,to_color=None,gradient='linear')  
	Sets the background for the info box. It can be a system's image or gradient going "from_color" to "to_color". By default all fields are "None" and only radial and linear gradients are supported.
###### set_info_text(title,subtitle,text)  
	Sets the information to show in the info box.  
	It must have a title, a subtitle and a text as arguments.  
###### set_info_text_fg(color)  
	Sets the foreground color of the info_text
###### get_action_area()  
	Returns the info box so we can add any widget to it.  
###### render_form()  
	Draws the screen and returns the box drawed.  
###### after_validation_goto()  
	Sets the function that the loginComponent will launch after a correct user's validation  
  
### Examples  
```python  
#!/usr/bin/env python3  
import gi  
gi.require_version('Gtk', '3.0')  
from gi.repository import Gtk  
from n4dgtklogin import *  
  
def _signin():  
	print("OK")  
	print("Now hide the login component and make things")  
  
def start_gui():  
	mw=Gtk.Window()  
	box=Gtk.Box()  
	loginComponent=N4dGtkLogin() #Init the login component  
	loginComponent.set_info_text("Title","Subtitle","Text text text.\nText text text:\n<sub>* text with sub tag</sub>")  
	loginComponent.set_info_text_fg("#000000")  
	#Uncomment and comment...
	##- Adding a widget to the info box
	#infobox=loginComponent.get_action_area()  
	#infobox.add(Gtk.Label("Add widget"))  
	##- Changing the background
	#loginComponent.set_info_background(from_color='#000000',to_color='@white',gradient='linear')  
	#loginComponent.set_info_background(image='/usr/share/backgrounds/ubuntu-mate-xenial/The_MATErix.png')  
	##- Changing default values for entries
	#loginComponent.set_default_username("Put your name")  
	#loginComponent.set_default_server("Put your server")  
	##- Changing banners
	#loginComponent.set_banner('/usr/share/filezilla/resources/flatzilla/48x48/uploadadd.png')  
	#loginComponent.set_info_banner('/usr/share/filezilla/resources/flatzilla/24x24/folder.png')  
	##- Function that will be launched after a succesfull validation
	loginComponent.after_validation_goto(_signin)  
	##- Render the form
	loginBox=loginComponent.render_form()
	##
	box.add(loginBox)  
	mw.add(box)  
	mw.connect("delete-event",Gtk.main_quit)  
	mw.show_all()  
  
start_gui()  
Gtk.main()  
```
