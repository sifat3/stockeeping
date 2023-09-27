# views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .models import Product, Purchase, Sale
from .forms import ProductForm, BuyProductForm, SellProductForm
from django.contrib.auth.decorators import login_required

from django.http import FileResponse
import io
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

from django.db.models import Sum
from datetime import datetime, timedelta, date
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
import base64

from django.contrib.auth import authenticate, login, logout
from django.contrib import messages


def purchase_product(request):
    products = Product.objects.all()
    
    if request.method == 'POST':
        form = BuyProductForm(request.POST)
        if form.is_valid():
            product_id = form.cleaned_data['product']
            quantity = form.cleaned_data['quantity']
            
            product = Product.objects.get(pk=product_id)
            unit_price = product.unit_buying_price
            
            # Calculate purchase price
            purchase_price = unit_price * quantity
            
            # Update form with calculated purchase price
            # form.data['purchase_price'] = purchase_price
            form.is_bound = True
            
            if product_id and quantity:
                product.quantity += quantity
                product.save()
                
                # Save the purchase record
                Purchase.objects.create(product=product, quantity=quantity)
                
                return redirect('view_inventory')
    else:
        form = BuyProductForm()
        # form.fields['product'].choices = [(product.id, product.name) for product in products]

    return render(request, 'buy_product.html', {'form': form})


def sell_product(request):
    if request.method == 'POST':
        form = SellProductForm(request.POST)
        if form.is_valid():
            product_id = form.cleaned_data['product']
            quantity = form.cleaned_data['quantity']
            # additional_details = form.cleaned_data['additional_details']

            # Get the selected product
            product = Product.objects.get(pk=product_id)
            # unit_price = product.unit_selling_price

            # Check if there is sufficient quantity to sell
            if product.quantity >= quantity:
                # Calculate sale price
                # sale_price = unit_price * quantity
                profit = ((product.unit_selling_price * quantity) - (product.unit_buying_price * quantity))
                # Update product quantity and save
                product.quantity -= quantity
                product.save()

                # Save the sale record
                Sale.objects.create(product=product, quantity=quantity, profit=profit)

                buf = io.BytesIO()
                doc = SimpleDocTemplate(buf, pagesize=letter)
                styles = getSampleStyleSheet()
                story = []

                # Title
                title_style = styles['Title']
                title_style.textColor = colors.red
                title = Paragraph("M/S Aleya Filling Station", title_style)
                story.append(title)

                # Subtitle
                subtitle_style = styles['Heading2']
                subtitle_style.textColor = colors.blue
                subtitle = Paragraph("For Customer", subtitle_style)
                story.append(subtitle)

                # Content
                content_style = styles['Heading4']
                lines = [
                    f"Product: {product.name}",
                    f"Quantity: {quantity} Liter",
                    f"Price: {(product.unit_selling_price * quantity)} taka"
                ]
                for line in lines:
                    content = Paragraph(line, content_style)
                    story.append(content)

                # Add the first image
                image1 = Image('static/image/img2.png', width=400, height=300)  # Replace with the actual path to your image
                story.append(image1)

                image2 = Image('static/image/img1.png', width=200, height=150)  # Replace with the actual path to your image
                story.append(image2)

                # Build the PDF document
                doc.build(story)
                buf.seek(0)

                # Send the PDF as a response
                return FileResponse(buf, as_attachment=True, filename="invoice.pdf")


            else:
                form.add_error('quantity', 'মজুদ অপর্যাপ্ত পরিমাণ।')


    else:
        form = SellProductForm()

    return render(request, 'sell_product.html', {'form': form})


 
@login_required(login_url='login')
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('view_inventory')  # Redirect to the inventory view after adding a product
    else:
        form = ProductForm()
    
    return render(request, 'add_product.html', {'form': form})

def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect('view_inventory')
    else:
        form = ProductForm(instance=product)

    return render(request, 'edit_product.html', {'form': form})



def view_inventory(request):
    products = Product.objects.all()
    return render(request, 'inventory.html', {'products': products})


def calculate_statistics(queryset):
    profits = [sale.profit for sale in queryset]
    return profits


def home(request):
    return render(request, 'home.html', {'year': 2023})  # You can update the year dynamically


def daily_profit(request):
    today = datetime.now().date()
    today_queryset = Sale.objects.filter(sale_date=today)
    today_total = sum(calculate_statistics(today_queryset))

    # Initialize lists to store data for the graph
    dates = []
    profits = []

    # Loop through the past seven days, including today
    for day_offset in range(0, 7):
        # Calculate the date for the current day in the loop
        current_day = today - timedelta(days=day_offset)

        # Query sale records for the current day
        queryset = Sale.objects.filter(sale_date=current_day)

        # Calculate the profit for the current day
        total_profit = sum([sale.profit for sale in queryset])

        # Append the date and profit to the lists
        dates.append(current_day.strftime('%d-%m-%y'))
        profits.append(total_profit)

    # Reverse the lists to display data in chronological order
    dates = dates[::-1]
    profits = profits[::-1]

    # Create a single composite bar chart for the past seven days, including today
    plt.figure(figsize=(12, 6))
    plt.bar(dates, profits)
    plt.title('Daily Profit Comparison for the Past Seven Days (Including Today)')
    plt.xlabel('Date')
    plt.ylabel('Profit')
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Convert the plot to an image and embed it in the template
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plot_data = base64.b64encode(buffer.read()).decode()
    buffer.close()

    return render(request, 'daily_profit.html', {'plot_data': plot_data, 'today_total':today_total})



def weekly_profit(request):
    today = datetime.now().date()
    last_week = today - timedelta(weeks=1)
    queryset = Sale.objects.filter(sale_date__range=[last_week, today])
    total = sum(calculate_statistics(queryset))
    # Initialize lists to store data for the graph
    weeks = []
    profits = []

    # Loop through the past seven weeks, including the current week
    for week_offset in range(0, 7):
        # Calculate the start and end dates for the current week in the loop
        end_date = today - timedelta(weeks=week_offset * 1)
        start_date = end_date - timedelta(days=6)

        # Query sale records for the current week
        queryset = Sale.objects.filter(sale_date__range=[start_date, end_date])

        # Calculate the profit for the current week
        total_profit = sum([sale.profit for sale in queryset])

        # Format the week range for the label
        week_range = f"{start_date.strftime('%d-%m-%y')} - {end_date.strftime('%d-%m-%y')}"

        # Append the week range and profit to the lists
        weeks.append(week_range)
        profits.append(total_profit)

    # Reverse the lists to display data in chronological order
    weeks = weeks[::-1]
    profits = profits[::-1]

    # Create a single composite bar chart for the past seven weeks, including the current week
    plt.figure(figsize=(12, 6))
    plt.bar(weeks, profits)
    plt.title('Weekly Profit Comparison for the Past Seven Weeks (Including This Week)')
    plt.xlabel('Week Range')
    plt.ylabel('Profit')
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Convert the plot to an image and embed it in the template
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plot_data = base64.b64encode(buffer.read()).decode()
    buffer.close()

    return render(request, 'weekly_profit.html', {'plot_data': plot_data, 'weekly_total':total})




def monthly_profit(request):
    today = datetime.now().date()
    last_month = today - timedelta(days=30)
    queryset = Sale.objects.filter(sale_date__range=[last_month, today])
    total = sum(calculate_statistics(queryset))

    # Initialize lists to store data for the graph
    months = []
    profits = []

    # Loop through the past seven months, including the current month
    for month_offset in range(0, 7):
        # Calculate the start and end dates for the current month in the loop
        end_date = today - timedelta(days=(today.day - 1)) - timedelta(weeks=month_offset * 4)
        start_date = end_date - timedelta(days=(end_date.day - 1))

        # Query sale records for the current month
        queryset = Sale.objects.filter(sale_date__range=[start_date, end_date])

        # Calculate the profit for the current month
        total_profit = sum([sale.profit for sale in queryset])

        # Format the month range for the label
        month_range = f"{start_date.strftime('%d-%m-%y')} - {end_date.strftime('%d-%m-%y')}" #%d-%m-%y

        # Append the month range and profit to the lists
        months.append(month_range)
        profits.append(total_profit)

    # Reverse the lists to display data in chronological order
    months = months[::-1]
    profits = profits[::-1]

    # Create a single composite bar chart for the past seven months, including the current month
    plt.figure(figsize=(12, 6))
    plt.bar(months, profits)
    plt.title('Monthly Profit Comparison for the Past Seven Months (Including This Month)')
    plt.xlabel('Month Range')
    plt.ylabel('Profit')
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Convert the plot to an image and embed it in the template
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plot_data = base64.b64encode(buffer.read()).decode()
    buffer.close()

    return render(request, 'monthly_profit.html', {'plot_data': plot_data, 'total':total})



def login_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            messages.info(request, 'Login successfull as SuperUser')
            return redirect('view_inventory')
        else:
            messages.info(request, 'Invalid Username or Password')
    return render(request, 'login.html')


def logout_user(request):
    logout(request)
    messages.info(request, 'Logged out successfully')
    return redirect('home')