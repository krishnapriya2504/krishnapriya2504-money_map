from flask import Flask, render_template, request, jsonify, redirect,url_for,send_file,flash
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os
import json

app = Flask(__name__)

# File path for storing data
DATA_FILE = 'data/transactions.json'

# Function to load transactions from the JSON file
def load_transactions():
    try:
        with open(DATA_FILE, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return []

# Function to save transactions to the JSON file
def save_transactions(data):
    with open(DATA_FILE, 'w') as file:
        json.dump(data, file)

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/income', methods=['GET', 'POST'])
def income():
    transactions = load_transactions()
    if request.method == 'POST':
        data = request.get_json()
        new_transaction = {
            'date': data['date'],  # Capture the date field
            'description': data['description'],
            'amount': data['amount'],
            'type': 'income'
        }
        transactions.append(new_transaction)
        save_transactions(transactions)
        return jsonify({'message': 'Income added successfully!'})
    return render_template('income.html')

@app.route('/expense', methods=['GET', 'POST'])
def expense():
    transactions = load_transactions()
    if request.method == 'POST':
        data = request.get_json()
        new_transaction = {
            'date': data['date'],  # Capture the date field
            'description': data['description'],
            'amount': data['amount'],
            'type': 'expense'
        }
        transactions.append(new_transaction)
        save_transactions(transactions)
        return jsonify({'message': 'Expense added successfully!'})
    return render_template('expense.html')
@app.route('/calendar')
def calendar():
    transactions = load_transactions()
    events = [
        {
            'title': t['description'],
            'start': t['date'],
            'type': t['type'],  # Distinguish between income and expense
            'amount': t['amount']  # Pass the amount for display
        }
        for t in transactions
    ]
    return render_template('calendar.html', events=events)

@app.route('/transactions', methods=['GET'])
def transaction_list():
    transactions = load_transactions()
    return render_template('transactions.html', transactions=transactions)

@app.route('/summary', methods=['GET'])
def summary():
    transactions = load_transactions()
    total_income = sum(item['amount'] for item in transactions if item['type'] == 'income')
    total_expense = sum(item['amount'] for item in transactions if item['type'] == 'expense')
    balance = total_income - total_expense
    return render_template('summary.html', income=total_income, expense=total_expense, balance=balance)

user_profile = {}

@app.route('/profile')
def profile():
    # Render the profile creation form
    return render_template('profile.html')

@app.route('/create-profile', methods=['POST'])
def create_profile():
    # Retrieve form data from the request
    name = request.form.get('name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    bio = request.form.get('bio')

    # Check if data exists
    if not name or not email or not phone:
        return "Error: All fields are required!", 400  # Send an error if required fields are missing

    # Save the data to the 'user_profile' dictionary (simulating a database)
    user_profile['name'] = name
    user_profile['email'] = email
    user_profile['phone'] = phone
    user_profile['bio'] = bio

    # Redirect to the page where the profile can be viewed
    return redirect(url_for('profile_view'))

@app.route('/profile-view')
def profile_view():
    # Check if the profile exists before rendering the view
    if not user_profile:
        return redirect(url_for('profile'))  # If profile doesn't exist, redirect to the profile form page

    return render_template('profile_view.html', profile=user_profile)

transactions = [
    {"date": "2024-12-01", "description": "Salary", "type": "income", "amount": 3000},
    {"date": "2024-12-02", "description": "Rent", "type": "expense", "amount": 1000},
    {"date": "2024-12-03", "description": "Groceries", "type": "expense", "amount": 200},
    {"date": "2024-12-04", "description": "Freelance", "type": "income", "amount": 500},
]

@app.route('/generate-report')
def generate_report():
    total_income = sum(t['amount'] for t in transactions if t['type'] == 'income')
    total_expense = sum(t['amount'] for t in transactions if t['type'] == 'expense')
    balance = total_income - total_expense
    return render_template(
        'generate_report.html',
        income=total_income,
        expense=total_expense,
        balance=balance,
        transactions=transactions
    )

@app.route('/download-pdf')
def download_pdf():
    # Generate PDF in-memory
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    pdf.setTitle("Transaction Report")

    # Title
    pdf.setFont("Helvetica-Bold", 20)
    pdf.drawString(200, 750, "Transaction Report")

    # Summary Section
    total_income = sum(t['amount'] for t in transactions if t['type'] == 'income')
    total_expense = sum(t['amount'] for t in transactions if t['type'] == 'expense')
    balance = total_income - total_expense

    pdf.setFont("Helvetica", 12)
    pdf.drawString(50, 700, f"Total Income: ${total_income}")
    pdf.drawString(50, 680, f"Total Expense: ${total_expense}")
    pdf.drawString(50, 660, f"Remaining Balance: ${balance}")

    # Transactions Table
    y = 640
    pdf.drawString(50, y, "Date")
    pdf.drawString(150, y, "Description")
    pdf.drawString(350, y, "Type")
    pdf.drawString(450, y, "Amount")
    y -= 20

    for transaction in transactions:
        pdf.drawString(50, y, transaction['date'])
        pdf.drawString(150, y, transaction['description'])
        pdf.drawString(350, y, transaction['type'].capitalize())
        pdf.drawString(450, y, f"${transaction['amount']}")
        y -= 20
        if y < 50:  # Add a new page if content exceeds page length
            pdf.showPage()
            y = 750

    pdf.save()
    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name="Transaction_Report.pdf",
        mimetype="application/pdf"
    )




@app.route('/chart')
def chart():
    transactions = load_transactions()
    total_income = sum(t['amount'] for t in transactions if t['type'] == 'income')
    total_expense = sum(t['amount'] for t in transactions if t['type'] == 'expense')
    balance = total_income - total_expense

    # Prepare summary data for the chart
    summary_data = {
        'income': total_income,
        'expense': total_expense,
        'balance': balance
    }

    # Send the full transaction list for the chart
    transaction_data = [
        {
            "date": t['date'],
            "type": t['type'],
            "amount": t['amount']
        }
        for t in transactions
    ]

    return render_template(
        'chart.html',
        summary_data=summary_data,
        transaction_data=transaction_data
    )

# File path for storing settings
SETTINGS_FILE = 'data/settings.json'


# Function to load settings
def load_settings():
    try:
        with open(SETTINGS_FILE, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {'theme': 'light'}  # Default theme is light

# Function to save settings
def save_settings(data):
    with open(SETTINGS_FILE, 'w') as file:
        json.dump(data, file)


@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if request.method == 'POST':
        theme = request.form.get('theme')
        settings = {'theme': theme}
        save_settings(settings)
        return redirect(url_for('settings'))

    settings = load_settings()
    return render_template('settings.html', settings=settings)


if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))  # Use the port assigned by the hosting service
    app.run(host='0.0.0.0', port=port)        # Run the app on the correct host and port
