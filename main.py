from kivy.app import App
from kivy.lang import Builder
from kivy.properties import NumericProperty, StringProperty, BooleanProperty,\
	ListProperty, ObjectProperty 
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.textinput import TextInput
import xml.etree.ElementTree as ET
import os
import urllib

Builder.load_string("""
#:kivy 1.8.0
<MainScreen>:
	BoxLayout:
		spacing: 20
		orientation: 'vertical'
		BoxLayout:
			size_hint_y: 0.3
			orientation: 'horizontal'
			BoxLayout:
				orientation: 'horizontal'
				BoxLayout:
					size_hint_x: 0.4
					orientation: 'vertical'
					Label:
						text: 'Address'
					Label:
						text: 'Address2'
					Label:
						text: 'City'
					Label:
						text: 'Postal Code'
					Label:
						text: 'State'
					Label:
						text: 'Country'
				BoxLayout:
					orientation: 'vertical'
					TextInput:
						id: out_addr
					TextInput:
						id: out_addr2
					TextInput:
						id: out_city
					TextInput:
						id: out_pcode
					TextInput:
						id: out_state
					TextInput:
						id: out_ctry
				BoxLayout:
					size_hint_x: 0.4
					orientation: 'vertical'
					Label:
						text: 'Latitude'
					Label:
						text: 'Longitude'
					Label:
						text: ''
					Label:
						text: ''
					Label:
						text: ''
					Label:
						text: ''
				BoxLayout:
					orientation: 'vertical'
					TextInput:
						id: out_lat
					TextInput:
						id: out_long
					Button:
						size_hint_y: 3
						text: 'Map Address'
				BoxLayout:
					orientation: 'vertical'
					Button:
						text: 'Options'
					Button:
						text: 'Send'
		BoxLayout:
			orientation: 'horizontal'
			BoxLayout:
				Label:
					text: ''
			Button:  
				size_hint_x: 3
				text: 'Map'

<OptionsScreen>:
	BoxLayout:
		orientation: 'vertical'
		TabbedPanel:
			do_default_tab: False
			TabbedPanelItem:
				text: 'Input'
				BoxLayout:
					orientation: 'vertical'
					BoxLayout:
						size_hint_y: 0.2
						BoxLayout:
							size_hint_x: 0.3
							orientation: 'vertical'
							Label:
								text: 'IP Address'
							Label:
								text: 'Port'
						BoxLayout:
							orientation: 'vertical'
							TextInput:
							TextInput:
					Label:
						size_hint_y: 0.1
						text: 'Message Format:'
					TextInput:
						id: in_format
						multiline: True
					BoxLayout:
						orientation: 'vertical'
						size_hint_y: 0.4
						Label:
							text: 'Address: %addr%'
						Label:
							text: 'City: %city%'
						Label:
							text: 'State: %state%'
						Label:
							text: 'Postal Code: %postcode%'
						Label:
							text: 'Country: %country%'
						Label:
							text: 'Country: %latitude%'
						Label:
							text: 'Country: %longitude%'
			TabbedPanelItem:
				text: 'Output'
		BoxLayout:
			size_hint_y: 0.075
			size_hint_x: 0.5
			pos_hint: {'right': 1}
			Button:
				text: 'Default'
			Button:
				text: 'Cancel'
				on_press: root.manager.current = 'main'
			Button:
				text: 'Save'
			Button:
				text: 'Accept'
				on_press: root.manager.current = 'main'
""")

class ResultButton(Button):
	disp = StringProperty()
	addr = StringProperty()
	addr2 = StringProperty()
	city = StringProperty()
	pcode = StringProperty()
	state = StringProperty()
	ctry = StringProperty()
	lat = StringProperty()
	lon = StringProperty()

class MainScreen(Screen):
	root_url = 'http://nominatim.openstreetmap.org/search?format=xml&addressdetails=1'
	def get_results(self):
		self.ids.result_list.clear_widgets()
		search_url = self.root_url
		search_url += '&street=' + self.ids.in_street.text
		search_url += '&city=' + self.ids.in_city.text
		search_url += '&state=' + self.ids.in_state.text
		search_url += '&postal_code=' + self.ids.in_pcode.text
		search_url += '&country=' + self.ids.in_ctry.text
		f = urllib.urlopen(search_url)
		page_source = f.read()
		result_xml = ET.fromstring(page_source)
		for result in result_xml:
			rbut = ResultButton()
			try:
				rbut.disp = result.get('display_name')
				rbut.addr = result.find('road').text
				rbut.addr2 = result.find('suburb').text
				rbut.city = result.find('city').text
				rbut.pcode = result.find('postcode').text
				rbut.state = result.find('state').text
				rbut.ctry = result.find('country').text
				rbut.lat = result.get('lat')
				rbut.lon = result.get('lon')
			except AttributeError:
				continue
			rbut.text = rbut.disp
			rbut.bind(on_press = self.result_selected(rbut))
			self.ids.result_list.add_widget(rbut)
		print result_xml.text

	def result_selected(self, rbut):
		self.ids.out_addr.text = rbut.addr
		self.ids.out_addr2.text = rbut.addr2
		self.ids.out_city.text = rbut.city
		self.ids.out_pcode.text = rbut.pcode
		self.ids.out_state.text = rbut.state
		self.ids.out_ctry.text = rbut.ctry
		self.ids.out_lat.text = rbut.lat
		self.ids.out_long.text = rbut.lon

	def pack_xml(self, tag, value):
		return('<' + tag + '>' + value + '</' + tag + '>')

	def next_field(self, current_field):
		field_array = [self.ids.in_street, self.ids.in_city, self.ids.in_state, self.ids.in_pcode, 
			self.ids.in_ctry, self.ids.out_addr, self.ids.out_addr2, self.ids.out_city, 
			self.ids.out_pcode, self.ids.out_state, self.ids.out_ctry, self.ids.out_lat, self.ids.out_long]
		next_index = (field_array.index(current_field) + 1) % len(field_array)
		next_field = field_array[next_index]
		return next_field

	def send_button(self):
		send_msg = ''
		send_msg += self.pack_xml('ADDRESS', self.ids.out_addr.text)
		send_msg += self.pack_xml('ADDRESS2', self.ids.out_addr2.text)
		send_msg += self.pack_xml('CITY', self.ids.out_city.text)
		send_msg += self.pack_xml('POSTAL_CODE', self.ids.out_pcode.text)
		send_msg += self.pack_xml('STATE', self.ids.out_state.text)
		send_msg += self.pack_xml('COUNTRY', self.ids.out_ctry.text)
		send_msg += self.pack_xml('LATITUDE', self.ids.out_lat.text)
		send_msg += self.pack_xml('LONGITUDE', self.ids.out_long.text)
		send_msg += self.pack_xml('MAP_MESSAGE', send_msg)
		print send_msg

class OptionsScreen(Screen):
	def settings(self):
		f = file('settings.xml', 'r+')
		#self.ids.in_format.text = 

settings_file = """<default>
	<input>
		<port>
			3000
		</port>
		<format>
			"<MAPMSG><ADDRESS>%addr%</ADDRESS><CITY>%city%</CITY><POSTAL_CODE>%pcode%</POSTAL_CODE><STATE>%state%</STATE><COUNTRY>%ctry%</COUNTRY><LATITUDE>%lat%</LATITUDE><LONGITUDE>%long%</LONGITUDE>></MAPMSG>"
		</format>
	</input>
	<output>
		<ip_address>
			127.0.0.1
		</ip_address>
		<port>
			3000
		</port>
		<format>
			"<MAPMSG><ADDRESS>%addr%</ADDRESS><ADDRESS2>%addr2%</ADDRESS2><CITY>%city%</CITY><POSTAL_CODE>%pcode%</POSTAL_CODE><STATE>%state%</STATE><COUNTRY>%ctry%</COUNTRY><LATITUDE>%lat%</LATITUDE><LONGITUDE>%long%</LONGITUDE>></MAPMSG>"
		</format>
	</output>
	<flags>
		<listen>
			0
		</listen>
	</flags>
</default>
<user>
	<input>
		<port>
			3000
		</port>
		<format>
			"<MAPMSG><ADDRESS>%addr%</ADDRESS><CITY>%city%</CITY><POSTAL_CODE>%pcode%</POSTAL_CODE><STATE>%state%</STATE><COUNTRY>%ctry%</COUNTRY><LATITUDE>%lat%</LATITUDE><LONGITUDE>%long%</LONGITUDE>></MAPMSG>"
		</format>
	</input>
	<output>
		<ip_address>
			127.0.0.1
		</ip_address>
		<port>
			3000
		</port>
		<format>
			"<MAPMSG><ADDRESS>%addr%</ADDRESS><ADDRESS2>%addr2%</ADDRESS2><CITY>%city%</CITY><POSTAL_CODE>%pcode%</POSTAL_CODE><STATE>%state%</STATE><COUNTRY>%ctry%</COUNTRY><LATITUDE>%lat%</LATITUDE><LONGITUDE>%long%</LONGITUDE>></MAPMSG>"
		</format>
	</output>
	<flags>
		<listen>
			0
		</listen>
	</flags>
</user>
"""

sm = ScreenManager(transition = FadeTransition())
sm.add_widget(MainScreen(name = 'main'))
sm.add_widget(OptionsScreen(name ='options'))

class ZenithApp(App):
	def build(self):
		if not(os.path.isfile("settings.xml")):
			f = file("settings.xml", "w")
			f.write(settings_file)
			f.close()
		return sm
	
if __name__ == '__main__':
	ZenithApp().run()
