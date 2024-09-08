from bs4 import BeautifulSoup
import requests
import smtplib
import os
from dotenv import load_dotenv
import csv
from datetime import datetime
import time

load_dotenv()

def log_price(product_title, current_price):
    with open('price_log.csv', mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([datetime.now(), product_title, current_price])
    print("Price logged.")

def send_email(subject, message):
    try:
        with smtplib.SMTP(os.environ["SMTP_ADDRESS"], port=587) as connection:
            connection.starttls()
            connection.login(os.environ["EMAIL_ADDRESS"], os.environ["EMAIL_PASSWORD"])
            connection.sendmail(
                from_addr=os.environ["EMAIL_ADDRESS"],
                to_addrs=os.environ["EMAIL_RECIPIENTS"].split(','),
                msg=f"Subject:{subject}\n\n{message}".encode("utf-8")
            )
        print("Email sent!")
    except Exception as e:
        print(f"Error sending email: {e}")

def send_sms(message):
    print(f"SMS sent: {message}")

def schedule_report():
    with open('price_log.csv', mode='r') as file:
        reader = csv.reader(file)
        print("\nScheduled Price Report:")
        for row in reader:
            print(row)
    print("Scheduled report sent!")

products = [
    {"url": "https://www.amazon.com/dp/B075CYMYK6?psc=1&ref_=cm_sw_r_cp_ud_ct_FM9M699VKHTT47YD50Q6", "target_price": 70},
    {"url": "https://www.amazon.com/dp/B079QHML21", "target_price": 50},
    {"url": "https://www.amazon.com/dp/B083KK5W26", "target_price": 120},
]

def check_price(product_url, target_price):
    try:
        header = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36",
            "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8"
        }

        response = requests.get(product_url, headers=header)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, "html.parser")

        title = soup.find(id="productTitle").get_text().strip()
        price = soup.find(class_="a-offscreen").get_text()
        price_as_float = float(price.replace("$", "").replace(",", ""))

        log_price(title, price_as_float)

        print(f"Product: {title}")
        print(f"Price: ${price_as_float}")

        if price_as_float < target_price:
            message = f"{title} is now on sale for {price}!\n\n{product_url}"
            send_email("Amazon Price Alert!", message)
            send_sms(message)

        elif price_as_float > target_price:
            print(f"Price of {title} has increased to ${price_as_float}, no email sent.")

    except requests.exceptions.RequestException as e:
        print(f"Error retrieving data: {e}")
    except AttributeError as e:
        print("Error parsing the page, please check the page structure.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def monitor_prices():
    for product in products:
        check_price(product["url"], product["target_price"])

def user_menu():
    print("\nAmazon Price Tracker\n")
    print("1. Start price monitoring")
    print("2. View price log")
    print("3. Schedule a price report")
    print("4. Add new product to track")
    print("5. Exit")

def add_new_product():
    url = input("Enter the Amazon product URL: ")
    target_price = float(input("Enter your target price: "))
    products.append({"url": url, "target_price": target_price})
    print("Product added!")

def display_price_log():
    try:
        with open('price_log.csv', mode='r') as file:
            reader = csv.reader(file)
            print("\nPrice Log:")
            for row in reader:
                print(row)
    except FileNotFoundError:
        print("No price log available yet.")

def main():
    while True:
        user_menu()
        choice = input("Enter your choice: ")
        if choice == '1':
            print("Starting price monitoring...")
            while True:
                monitor_prices()
                time.sleep(21600) 
        elif choice == '2':
            display_price_log()
        elif choice == '3':
            schedule_report()
        elif choice == '4':
            add_new_product()
        elif choice == '5':
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
