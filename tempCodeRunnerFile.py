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