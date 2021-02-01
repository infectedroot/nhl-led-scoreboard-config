import flask, time, json, subprocess, requests
from distutils.util import strtobool
from scoreboard_config import ScoreboardConfig
from flask import request, jsonify, Flask, send_from_directory, render_template
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler

configFile = "/home/pi/nhl-led-scoreboard/config/config.json"

TEAMS     = ['Avalanche','Blackhawks','Blues','Blue Jackets','Bruins','Canadiens','Canucks','Capitals','Coyotes','Devils','Ducks','Flames','Flyers',
             'Golden Knights','Hurricanes','Islanders','Jets','Kings','Maple Leafs','Lightning','Oilers','Panthers','Penguins','Predators',
             'Rangers','Red Wings','Sabres','Senators','Sharks','Stars','Wild']

SECTIONS  = ['general','preferences','states','boards','sbio']
STATES    = ['off_day','scheduled','intermission','post_game']
BOARDS    = ['clock','weather','wxalert','scoreticker','seriesticker','standings','covid19']
BOARD2    = ['clock','weather','wxalert','wxforecast','scoreticker','seriesticker','standings','team_summary','covid_19','stanley_cup_champions','christmas']
SBIO      = ['pushbutton','dimmer','screensaver','mqtt']

US_STATES = ['Alabama','Alaska','Arizona','Arkansas','California','Colorado','Connecticut','Delaware','District Of Columbia','Florida','Georgia','Guam',
             'Hawaii','Idaho','Illinois','Indiana','Iowa','Kansas','Kentucky','Louisiana','Maine','Maryland','Massachusetts','Michigan','Minnesota',
             'Mississippi','Missouri','Montana','Nebraska','Nevada','New Hampshire','New Jersey','New Mexico','New York','North Carolina','North Dakota',
             'Northern Mariana Islands','Ohio','Oklahoma','Oregon','Pennsylvania','Puerto Rico','Rhode Island','South Carolina','South Dakota','Tennessee',
             'Texas','United States Virgin Islands','Utah','Vermont','Virginia','Washington','West Virginia','Wisconsin','Wyoming']

COUNTRIES = ['USA','Canada','China','Iran','Italy','France','Afghanistan','Albania','Algeria','Andorra','Angola','Anguilla','Antigua and Barbuda','Argentina','Armenia','Aruba','Australia',
             'Austria','Azerbaijan','Bahamas','Bahrain','Bangladesh','Barbados','Belarus','Belgium','Belize','Benin','Bermuda','Bhutan','Bolivia','Bosnia and Herzegovina','Botswana','Brazil',
             'British Virgin Islands','Brunei','Bulgaria','Burkina Faso','CAR','Cabo Verde','Cambodia','Cameroon','Cayman Islands','Chad','Channel Islands','Chile','Colombia','Congo',
             'Costa Rica','Croatia','Cuba','Curaçao','Cyprus','Czechia','DRC','Denmark','Diamond Princess','Djibouti','Dominica','Dominican Republic','Ecuador','Egypt','El Salvador','Equatorial Guinea',
             'Eritrea','Estonia','Eswatini','Ethiopia','Faeroe Islands','Fiji','Finland','French Guiana','French Polynesia','Gabon','Gambia','Georgia','Germany','Ghana','Gibraltar','Greece',
             'Greenland','Grenada','Guadeloupe','Guatemala','Guinea','Guinea-Bissau','Guyana','Haiti','Honduras','Hong Kong','Hungary','Iceland','India','Indonesia','Iraq','Ireland','Isle of Man',
             'Israel','Ivory Coast','Jamaica','Japan','Jordan','Kazakhstan','Kenya','Kuwait','Kyrgyzstan','Laos','Latvia','Lebanon','Liberia','Libya','Liechtenstein','Lithuania','Luxembourg',
             'MS Zaandam','Macao','Madagascar','Malaysia','Maldives','Mali','Malta','Martinique','Mauritania','Mauritius','Mayotte','Mexico','Moldova','Monaco','Mongolia','Montenegro','Montserrat',
             'Morocco','Mozambique','Myanmar','Namibia','Nepal','Netherlands','New Caledonia','New Zealand','Nicaragua','Niger','Nigeria','North Macedonia','Norway','Oman','Pakistan','Palestine',
             'Panama','Papua New Guinea','Paraguay','Peru','Philippines','Poland','Portugal','Qatar','Romania','Russia','Rwanda','Réunion','S. Korea','Saint Kitts and Nevis','Saint Lucia','Saint Martin',
             'San Marino','Saudi Arabia','Senegal','Serbia','Seychelles','Singapore','Sint Maarten','Slovakia','Slovenia','Somalia','South Africa','Spain','Sri Lanka','St. Barth','St. Vincent Grenadines',
             'Sudan','Suriname','Sweden','Switzerland','Syria','Taiwan','Tanzania','Thailand','Timor-Leste','Togo','Trinidad and Tobago','Tunisia','Turkey','Turks and Caicos','UAE','UK','Uganda',
             'Ukraine','Uruguay','Uzbekistan','Vatican City','Venezuela','Vietnam','Zambia','Zimbabwe']


CA_PROVS  = ['Alberta','British Columbia','Manitoba','New Brunswick','Newfoundland and Labrador','Northwest Territories','Nova Scotia','Ontario','Prince Edward Island','Quebec','Saskatchewan','Yukon']

GPIO_PINS = [2,3,7,8,9,10,11,14,15,19,24,25]

app = flask.Flask(__name__, static_url_path='', static_folder='.',template_folder='templates')
app.config["DEBUG"] = True

data = {}

@app.route('/',methods=('GET', 'POST'))
def index():
	if request.method == 'POST':
		if request.form["action"] == "reload":
			print("RELOAD")
			subprocess.run(["supervisorctl","restart","nhl-led-scoreboard"],stderr=subprocess.PIPE,stdout=subprocess.PIPE,universal_newlines=True)
		if request.form["action"] == "restart":
			print("RESTART")
			subprocess.run(["reboot"],stderr=subprocess.PIPE,stdout=subprocess.PIPE,universal_newlines=True)
		if request.form["action"] == "shutdown":
			print("SHUTDOWN")
			subprocess.run(["shutdown","-h", "now"],stderr=subprocess.PIPE,stdout=subprocess.PIPE,universal_newlines=True)
	scoreboardLogs = requests.get("http://127.0.0.1:9001/tail.html?processname=scoreboard&limit=1800")
	#scoreboardLogs = subprocess.run(["tail","'/var/log/supervisor/scoreboard-stdout*'"],stderr=subprocess.PIPE,stdout=subprocess.PIPE,universal_newlines=True)
	statMem = subprocess.run(["free","-m"],stderr=subprocess.PIPE,stdout=subprocess.PIPE,universal_newlines=True)
	statDisk = subprocess.run(["df","-h"],stderr=subprocess.PIPE,stdout=subprocess.PIPE,universal_newlines=True)
	statUptime = subprocess.run(["uptime"],stderr=subprocess.PIPE,stdout=subprocess.PIPE,universal_newlines=True)
	statNet = subprocess.run(["ifconfig"],stderr=subprocess.PIPE,stdout=subprocess.PIPE,universal_newlines=True)
	return render_template('overview.html', logs=scoreboardLogs.text, statMem=statMem, statDisk=statDisk, statUptime=statUptime,statNet=statNet)
	#return app.send_static_file('templates/overview.html')


@app.route("/prefs",methods=('GET', 'POST'))
def prefs():
	if request.method == 'POST':
		app.data["preferences"]["time_format"] = request.form["time_format"]
		app.data["preferences"]["end_of_day"] = request.form["end_of_day"]
		app.data["preferences"]["location"] = request.form["location"]
		app.data["preferences"]["live_game_refresh_rate"] = int(request.form["live_game_refresh_rate"])
		app.data["preferences"]["teams"] = request.form.getlist("teams[]")
		app.data["preferences"]["sog_display_frequency"] = int(request.form["sog_display_frequency"])
		app.data["preferences"]["goal_animations"]["pref_team_only"] = bool(strtobool(request.form["goal_animations"]))
		app.data["live_mode"] = bool(strtobool(request.form["live_mode"]))
		print(app.data["preferences"])
		save_config()
	reload_config(None)
	return render_template('nhl-prefs.html', data=app.data, teams=TEAMS)

@app.route("/states",methods=('GET', 'POST'))
def states():
	if request.method == 'POST':
		app.data["states"]["off_day"] = request.form.getlist("off_day_boards[]")
		app.data["states"]["scheduled"] = request.form.getlist("scheduled_boards[]")
		app.data["states"]["intermission"] = request.form.getlist("intermission_boards[]")
		app.data["states"]["post_game"] = request.form.getlist("post_game_boards[]")
		print(app.data["states"])
		save_config()
	reload_config(None)
	return render_template('nhl-states.html', data=app.data, boards=BOARD2, boards2=BOARD2)

@app.route("/config",methods=('GET', 'POST'))
def config():
	if request.method == 'POST':
		app.data["boards"]["scoreticker"]["preferred_teams_only"] = bool(strtobool(request.form["score_pref_teams"]))
		app.data["boards"]["scoreticker"]["rotation_rate"] = int(request.form["score_rotation_rate"])
		app.data["boards"]["seriesticker"]["preferred_teams_only"] = bool(strtobool(request.form["series_pref_teams"]))
		app.data["boards"]["seriesticker"]["rotation_rate"] = int(request.form["series_rotation_rate"])
		app.data["boards"]["standings"]["preferred_standings_only"] = bool(strtobool(request.form["standings_pref_teams"]))
		app.data["boards"]["standings"]["standing_type"] = request.form["standings_standing_type"]
		app.data["boards"]["standings"]["divisions"] = request.form["standings_divisions"]
		app.data["boards"]["standings"]["conference"] = request.form["standings_conference"]
		app.data["boards"]["clock"]["duration"] = int(request.form["clock_duration"])
		app.data["boards"]["clock"]["hide_indicator"] = bool(strtobool(request.form["clock_hide_indicator"]))
		#app.data["boards"]["clock"]["preferred_team_colors"] = bool(strtobool(request.form["clock_pref_teams"]))
		#app.data["boards"]["clock"]["clock_rgb"] = tuple(map(int, request.form["clock_clock_rgb"][4:-1].split(',')))
		#app.data["boards"]["clock"]["date_rgb"] = tuple(map(int, request.form["clock_date_rgb"][4:-1].split(',')))
		app.data["boards"]["clock"]["flash_seconds"] = bool(strtobool(request.form["clock_flash_seconds"]))
		app.data["boards"]["weather"]["enabled"] = bool(strtobool(request.form["weather_enabled"]))
		app.data["boards"]["weather"]["view"] = request.form["weather_view"]
		app.data["boards"]["weather"]["units"] = request.form["weather_units"]
		app.data["boards"]["weather"]["duration"] = int(request.form["weather_duration"])
		app.data["boards"]["weather"]["owm_apikey"] = request.form["weather_owm_apikey"]
		app.data["boards"]["weather"]["update_freq"] = int(request.form["weather_update_freq"])
		app.data["boards"]["weather"]["show_on_clock"] = bool(strtobool(request.form["weather_show_on_clock"]))
		app.data["boards"]["weather"]["forecast_enabled"] = bool(strtobool(request.form["weather_forecast_enabled"]))
		app.data["boards"]["weather"]["forecast_days"] = int(request.form["weather_forecast_days"])
		app.data["boards"]["weather"]["forecast_update"] = int(request.form["weather_forecast_update"])
		app.data["boards"]["wxalert"]["alert_feed"] = request.form["wxalert_alert_feed"]
		app.data["boards"]["wxalert"]["update_freq"] = int(request.form["wxalert_update_freq"])
		app.data["boards"]["wxalert"]["show_alerts"] = bool(strtobool(request.form["wxalert_show_alerts"]))
		app.data["boards"]["wxalert"]["nws_show_expire"] = bool(strtobool(request.form["wxalert_nws_show_expire"]))
		app.data["boards"]["wxalert"]["alert_title"] = bool(strtobool(request.form["wxalert_alert_title"]))
		app.data["boards"]["wxalert"]["scroll_alert"] = bool(strtobool(request.form["wxalert_scroll_alert"]))
		app.data["boards"]["wxalert"]["alert_duration"] = int(request.form["wxalert_alert_duration"])
		app.data["boards"]["wxalert"]["show_on_clock"] = bool(strtobool(request.form["wxalert_show_on_clock"]))
		save_config()
	reload_config(None)
	return render_template('nhl-config.html', data=app.data)

@app.route("/sbio",methods=('GET', 'POST'))
def sbio():
	if request.method == 'POST':
		app.data["sbio"]["dimmer"]["enabled"] = bool(strtobool(request.form["dimmer_enabled"]))
		app.data["sbio"]["dimmer"]["mode"] = request.form["dimmer_mode"]
		app.data["sbio"]["dimmer"]["daytime"] = request.form["dimmer_daytime"]
		app.data["sbio"]["dimmer"]["nighttime"] = request.form["dimmer_nighttime"]
		app.data["sbio"]["dimmer"]["sunset_brightness"] = int(request.form["sunset_brightness"])
		app.data["sbio"]["dimmer"]["sunrise_brightness"] = int(request.form["sunrise_brightness"])
		save_config()
	reload_config(None)
	return render_template('nhl-sbio.html', data=app.data)

@app.route("/advanced",methods=('GET', 'POST'))
def advanced():
	if request.method == 'POST':
		if request.form["remote_control"] == "1":
			subprocess.run(["systemctl","restart","openvpn"],stdout=subprocess.PIPE,universal_newlines=True)
		else:
			subprocess.run(["systemctl","stop","openvpn"],stdout=subprocess.PIPE,universal_newlines=True)
	isRemote = subprocess.run(["systemctl","status","openvpn"],stdout=subprocess.PIPE,universal_newlines=True)
	return render_template('nhl-advanced.html', data=app.data, isRemote=isRemote)

@app.route('/js/<path:path>')
def send_js(path):
	return send_from_directory('js', path)

@app.route('/css/<path:path>')
def send_css(path):
	return send_from_directory('css', path)

def reload_config(event):
    with open(configFile) as f:
        app.data = json.load(f)

def save_config():
	f = open(configFile, "w")
	f.write(json.dumps(app.data, indent = 4))
	f.close()

if __name__ == "__main__":

    my_event_handler = PatternMatchingEventHandler("*")
    my_event_handler.on_modified = reload_config

    path = configFile
    my_observer = Observer()
    my_observer.schedule(my_event_handler, path)
    my_observer.start()

    with open(configFile) as f:
        app.data = json.load(f)

	# Output: {'name': 'Bob', 'languages': ['English', 'Fench']}
    print(app.data)

    print(json.dumps(app.data, indent = 4))
    # validate json config
    # load json config
    app.run(host='0.0.0.0', port=80)
