# from flask import Flask, render_template, request, redirect, url_for

# app = Flask(__name__)

# # In-memory "database" (for now)
# crop_data = []

# @app.route("/")
# def index():
#     return render_template("index.html", crops=crop_data)

# @app.route("/add-crop", methods=["GET", "POST"])
# def add_crop():
#     if request.method == "POST":
#         # Get data from the form
#         crop_name = request.form["crop_name"]
#         planting_date = request.form["planting_date"]
#         harvest_date = request.form["harvest_date"]

#         # Save to "database"
#         crop_data.append({
#             "crop_name": crop_name,
#             "planting_date": planting_date,
#             "harvest_date": harvest_date
#         })
#         return redirect(url_for("index"))

#     return render_template("add_crop.html")

# if __name__ == "__main__":
#     app.run(debug=True)



# from flask import Flask, render_template, request

# app = Flask(__name__)

# crops = []

# # Homepage route
# @app.route('/')
# def index():
#     # return render_template('index.html', crops=crops)
#     sort_order = request.args.get('sort')  # Get the sort query parameter

#     # Sort crops by planting date
#     if sort_order == 'asc':
#         sorted_crops = sorted(crops, key=lambda x: x['date'])  # Ascending order
#     elif sort_order == 'desc':
#         sorted_crops = sorted(crops, key=lambda x: x['date'], reverse=True)  # Descending order
#     else:
#         sorted_crops = crops  # No sorting

#     return render_template('index.html', crops=sorted_crops)  # Pass sorted crops to template

# # Add crop route

# @app.route('/add_crop', methods=['GET', 'POST'])
# def add_crop():
#     if request.method == 'POST':
#         # Handle form submission (we'll add functionality later)
#         crop_name = request.form['crop_name']
#         planting_date = request.form['planting_date']
#         crops.append({'name': crop_name, 'date': planting_date})
#         # Save crop data (for now, just print it)
#         print(f"Crop added: {crop_name}, Planting Date: {planting_date}")
#         return render_template('add_crop.html', success=True)
#     return render_template('add_crop.html')


# if __name__ == '__main__':
#     app.run(debug=True)

from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect
import requests
from flask_sqlalchemy import SQLAlchemy

# Initialize Flask app
app = Flask(__name__)

# Configure the database URI
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///farmflow.db'  # Use SQLite database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy with the app
db = SQLAlchemy(app)

# Define Equipment model
class Equipment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    usage_date = db.Column(db.Date, nullable=False)
    maintenance_date = db.Column(db.Date, nullable=False)

# Initialize an empty list of crops (this will act as your "database" for now)
crops = []

# Weather function to get data from OpenWeatherMap
def get_weather(location):
    api_key = '72cfb1fd186ca00e5239d3a91e826d04' 
    url = f'http://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}&units=metric'
    
    # Corrected: use requests.get() instead of request.get()
    response = requests.get(url)
    data = response.json()

    if data.get('cod') != 200:
        return None  # If there's an error fetching the data (e.g., city not found)
    
    weather_info = {
        'location': data['name'],  # Display the name of the city
        'temperature': data['main']['temp'],
        'humidity': data['main']['humidity'],
        'description': data['weather'][0]['description'],
    }
    return weather_info

# Homepage route
@app.route('/', methods=['GET', 'POST'])
def index():
    weather = None
    if request.method == 'POST':
        location = request.form.get('location')  # Get location from the form
        if location:
            weather = get_weather(location)  # Fetch weather for the user's location
    
    sort_order = request.args.get('sort')  # Get the sort query parameter

    # Sort crops by planting date
    if sort_order == 'asc':
        sorted_crops = sorted(crops, key=lambda x: x['date'])  # Ascending order
    elif sort_order == 'desc':
        sorted_crops = sorted(crops, key=lambda x: x['date'], reverse=True)  # Descending order
    else:
        sorted_crops = crops  # No sorting

    return render_template('index.html', crops=sorted_crops, weather=weather)


# Add crop route
# @app.route('/add_crop', methods=['GET', 'POST'])
# def add_crop():
#     if request.method == 'POST':
#         # Handle form submission
#         crop_name = request.form['crop_name']
#         planting_date = request.form['planting_date']
#         # Save crop data in the crops list (acting as a database for now)
#         crops.append({'name': crop_name, 'date': planting_date})
#         return redirect('/')  # Redirect to homepage after adding crop
#     return render_template('add_crop.html')

@app.route('/add_crop', methods=['GET', 'POST'])
def add_crop():
    if request.method == 'POST':
        name = request.form['name']
        planting_date = request.form['date']
        growing_period = int(request.form['growing_period'])  # Growing period in days

        # Ensure valid date format
        try:
            planting_date_obj = datetime.strptime(planting_date, '%Y-%m-%d')
            harvest_date = planting_date_obj + timedelta(days=growing_period)
        except ValueError:
            # Handle invalid date input
            harvest_date = None  # You can set a default or show an error message

        # Add crop data (ensure harvest_date is passed correctly)
        crops.append({
            'name': name,
            'date': planting_date,
            'growing_period': growing_period,
            'harvest_date': harvest_date.strftime('%Y-%m-%d') if harvest_date else '2025-01-01'
        })

        return redirect('/')
    return render_template('add_crop.html')


# Edit crop route
@app.route('/edit_crop/<int:index>', methods=['GET', 'POST'])
def edit_crop(index):
    crop = crops[index]  # Retrieve the crop by index
    if request.method == 'POST':
        # Update crop data
        crop['name'] = request.form['crop_name']
        crop['date'] = request.form['planting_date']
        return redirect('/')  # Redirect to homepage after saving
    return render_template('edit_crop.html', crop=crop, crop_index=index)

# Delete crop route
@app.route('/delete_crop/<int:index>')
def delete_crop(index):
    crops.pop(index)  # Remove the crop from the list
    return redirect('/')  # Redirect to homepage after deleting the crop

# Crop Health Monitoring route
@app.route('/crop_health/<int:index>', methods=['GET', 'POST'])
def crop_health(index):
    crop = crops[index]  # Get the crop by index
    
    if request.method == 'POST':
        health_status = request.form['health_status']
        pest_issues = request.form['pest_issues']
        growth_stage = request.form['growth_stage']
        notes = request.form['notes']
        
        # Save the health information in the crop data
        crop['health'] = {
            'status': health_status,
            'pests': pest_issues,
            'growth_stage': growth_stage,
            'notes': notes,
        }
        
        return redirect('/')  # Redirect back to the homepage after submitting

    return render_template('crop_health.html', crop=crop, index=index)

@app.route('/resource_management/<int:index>', methods=['GET', 'POST'])
def resource_management(index):
    crop = crops[index]  # Get the crop by index
    
    if request.method == 'POST':
        # Gather resource data from the form
        water_usage = request.form['water_usage']
        fertilizer_usage = request.form['fertilizer_usage']
        soil_health = request.form['soil_health']
        
        # Save the resource data to the crop
        if 'resources' not in crop:
            crop['resources'] = []
        crop['resources'].append({
            'water': water_usage,
            'fertilizer': fertilizer_usage,
            'soil': soil_health,
        })
        
        return redirect('/')  # Redirect back to homepage

    return render_template('resource_management.html', crop=crop, index=index)

# Initialize a list to store financial records
financial_records = []

@app.route('/financial_tracker', methods=['GET', 'POST'])
def financial_tracker():
    if request.method == 'POST':
        # Handle form submission
        record_type = request.form['type']  # "income" or "expense"
        amount = float(request.form['amount'])
        description = request.form['description']
        date = request.form['date']

        # Save the financial record
        financial_records.append({
            'type': record_type,
            'amount': amount,
            'description': description,
            'date': date
        })
        return redirect('/financial_tracker')  # Redirect to refresh the page

    # Calculate total income and expenses
    total_income = sum(record['amount'] for record in financial_records if record['type'] == 'income')
    total_expenses = sum(record['amount'] for record in financial_records if record['type'] == 'expense')
    net_profit = total_income - total_expenses

    return render_template(
        'financial_tracker.html',
        records=financial_records,
        total_income=total_income,
        total_expenses=total_expenses,
        net_profit=net_profit
    )

@app.route('/calendar')
def calendar():
    return render_template('calendar.html', crops=crops)

# In-memory list to store equipment logs
equipment_logs = []

# Route for logging equipment usage and maintenance
@app.route('/equipment', methods=['GET', 'POST'])
def equipment():
    if request.method == 'POST':
        # Get data from the form
        equipment_name = request.form['equipment_name']
        usage_date = request.form['usage_date']
        next_maintenance = request.form['next_maintenance']

        # Convert the date strings to date objects
        usage_date_obj = datetime.strptime(usage_date, '%Y-%m-%d').date()
        next_maintenance_obj = datetime.strptime(next_maintenance, '%Y-%m-%d').date()

        # Add the equipment to the database
        new_equipment = Equipment(
            name=equipment_name, 
            usage_date=usage_date_obj, 
            maintenance_date=next_maintenance_obj
        )
        db.session.add(new_equipment)
        db.session.commit()

        return redirect('/equipment')

    # This will be executed for the GET request, to display equipment logs
    equipment_logs = Equipment.query.all()

    return render_template('equipment.html', equipment_logs=equipment_logs)

@app.route('/edit_equipment/<int:id>', methods=['GET', 'POST'])
def edit_equipment(id):
    equipment = Equipment.query.get(id)  # Fetch the equipment by ID
    if request.method == 'POST':
        equipment.name = request.form['name']
        equipment.usage_date = datetime.strptime(request.form['usage_date'], '%Y-%m-%d').date()
        equipment.maintenance_date = datetime.strptime(request.form['maintenance_date'], '%Y-%m-%d').date()

        db.session.commit()
        return redirect('/equipment')  # Redirect to the equipment log page after saving changes

    return render_template('edit_equipment.html', equipment=equipment)

@app.route('/delete_equipment/<int:id>', methods=['POST'])
def delete_equipment(id):
    equipment = Equipment.query.get_or_404(id)  # Fetch equipment by ID or return 404
    db.session.delete(equipment)
    db.session.commit()  # Save changes
    return redirect('/equipment')

@app.route('/sustainability_tracker', methods=['GET', 'POST'])
def sustainability_tracker():
    carbon_footprint = None
    if request.method == 'POST':
        # Get inputs from the form
        energy_usage = float(request.form['energy_usage'])
        fuel_consumption = float(request.form['fuel_consumption'])
        machinery_use = float(request.form['machinery_use'])

        # Define the emissions factors (these values would depend on the farm's specific region and energy mix)
        # Example: Emission factor for electricity in kWh (e.g., 0.5 kg CO2e per kWh)
        emission_factor_energy = 0.5  # kg CO2e per kWh
        emission_factor_fuel = 2.5  # kg CO2e per liter of fuel
        emission_factor_machinery = 0.1  # kg CO2e per hour of machinery use

        # Calculate the carbon footprint
        carbon_footprint = (energy_usage * emission_factor_energy) + \
                           (fuel_consumption * emission_factor_fuel) + \
                           (machinery_use * emission_factor_machinery)

        # Return the calculated footprint in the template
        return render_template('sustainability_tracker.html', carbon_footprint=carbon_footprint)

    return render_template('sustainability_tracker.html')
@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True)

