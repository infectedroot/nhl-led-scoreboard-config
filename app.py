import flask, time, json
from scoreboard_config import ScoreboardConfig
from flask import request, jsonify, Flask, send_from_directory, render_template

configFile = "config.json.sample"

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

@app.route('/')
def index():
	posts = ""
	return render_template('overview.html', posts=posts)
	#return app.send_static_file('templates/overview.html')


@app.route("/prefs")
def prefs():
	return render_template('nhl-prefs.html', data=data, teams=TEAMS)

@app.route("/states",methods=('GET', 'POST'))
def states():
	return render_template('nhl-states.html', boards=BOARDS, boards2=BOARD2)

@app.route("/config")
def config():
	return render_template('nhl-config.html')

@app.route("/sbio")
def sbio():
	return render_template('nhl-sbio.html')

@app.route("/advanced")
def advanced():
	return render_template('nhl-advanced.html')

@app.route('/js/<path:path>')
def send_js(path):
	return send_from_directory('js', path)

@app.route('/css/<path:path>')
def send_css(path):
	return send_from_directory('css', path)

if __name__ == "__main__":
	with open(configFile) as f:
		data = json.load(f)

	# Output: {'name': 'Bob', 'languages': ['English', 'Fench']}
	print(data)

	print(json.dumps(data, indent = 4))
	# validate json config
	# load json config
	app.run(host='0.0.0.0')
