import asyncio
import sys
from upload import upload_to_folder
from save import save_to_database
from fuzzywuzzy import fuzz
from datetime import datetime, timedelta
import random 
from playwright.sync_api import sync_playwright 
import os 
import time 
import pandas as pd
from datetime import datetime
import pycountry
from discord_bot import create_discord_client, run_discord_client

download_dir = r"path/to/your/download/directory"
debugging_url = 'Your_personal_web_socket_local_url'
seller_ids_list = ['Example_seller_id']
start_date = '2024-01-01'
end_date = '2024-01-10'
launcher='enter_yourname_here'

def date_generator(start_date, end_date):
    start_date = datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.strptime(end_date, '%Y-%m-%d')
    generated_dates = []
    current_date = start_date
    while current_date <= end_date:
        generated_dates.append(current_date.strftime('%Y-%m-%d'))
        current_date += timedelta(days=1)
    return generated_dates

def getting_calendar_year_month(month_string):
    month_string = month_string.strip().lower()
    full_month_name = month_string.split('-')[1]

    month_map = {
        'january': 1, 'feburary': 2, 'march': 3, 'april': 4,
        'may': 5, 'june': 6, 'july': 7, 'august': 8,
        'september': 9, 'october': 10, 'november': 11, 'december': 12
    }

    month_number = month_map.get(full_month_name)

    if month_number:
        first_day_of_month = datetime(datetime.now().year, month_number, 1)
        return first_day_of_month
    else:
        return None

def getting_search_list(): 
    current_directory = os.getcwd() 
    file_name = 'BP_dict.xlsx'
    file_path = os.path.join(current_directory, file_name) 
    df = pd.read_excel(file_path)
    seller_type_list = df['seller_type'].tolist()
    seller_used_id_list = df['seller_used_id'].tolist()
    seller_name_list = df['name'].tolist()
    result_list = []
    for index in range(len(seller_type_list)): 
        data_point = {
            'seller_type': seller_type_list[index],
            'seller_used_id': seller_used_id_list[index],
            'seller_name': seller_name_list[index]
        }
        result_list.append(data_point)
    return result_list 

def getting_working_list(seller_ids_list, search_list):
    working_list = []
    for seller_id in seller_ids_list:
        for iterated_dict in search_list: 
            iterated_seller_id = iterated_dict.get('seller_used_id', '')
            if iterated_seller_id == seller_id: 
                seller_type = iterated_dict.get('seller_type', '')
                seller_name = iterated_dict.get('seller_name', '')
                search_dict = { 
                    'seller_id': iterated_seller_id, 
                    'seller_type': seller_type, 
                    'seller_name': seller_name
                }
        working_list.append(search_dict)
    return working_list

def getting_country(seller_used_id): 
    country = seller_used_id.split('.')[0]
    country_object = pycountry.countries.get(alpha_2=country)
    if country_object: 
            country_name = country_object.name 
            if country_name == 'Viet Nam': 
                country_name = 'Vietnam'
    return country_name

def hovering_date(day_button, page): 
    while True: 
        try: 
            day_button.hover() 
            calendar_object = page.query_selector('div.oui-date-picker-menu.open')
            if calendar_object: 
                return calendar_object
            elif not calendar_object:
                continue
        except Exception: 
            continue 

def box_validations(page): 
    validated_button = 0
    span_country_list = []
    span_channel_list = []
    span_store_list = []
    while True: 
        all_menus = page.query_selector_all('ul.my-cascader-menu')
        try: 
            country_li_elements = all_menus[0].query_selector_all('li')
            channel_li_elements = all_menus[1].query_selector_all('li')
            store_li_elements = all_menus[2].query_selector_all('li')
            break
        except Exception:
            continue  
    for li_element in country_li_elements: 
        span_elements = li_element.query_selector_all('span')[0].get_attribute('class')
        span_country_list.append(span_elements)
    for li_element in channel_li_elements: 
        span_elements = li_element.query_selector_all('span')[0].get_attribute('class')
        span_channel_list.append(span_elements)
    for li_element in store_li_elements: 
        span_elements = li_element.query_selector_all('span')[0].get_attribute('class')
        span_store_list.append(span_elements)   
    if span_country_list.count('my-cascader-checkbox my-cascader-checkbox-checked') == 1 or \
        span_country_list.count('my-cascader-checkbox my-cascader-checkbox-indeterminate') == 1: 
        validated_button += 1
    if span_channel_list.count('my-cascader-checkbox my-cascader-checkbox-checked') == 1 or \
        span_channel_list.count('my-cascader-checkbox my-cascader-checkbox-indeterminate') == 1:
        validated_button += 1
    if span_store_list.count('my-cascader-checkbox my-cascader-checkbox-checked') == 1 or \
        span_store_list.count('my-cascader-checkbox my-cascader-checkbox-indeterminate') == 1: 
        validated_button += 1
    return validated_button
        
search_list = getting_search_list()
working_list = getting_working_list(seller_ids_list, search_list)
missing_days = date_generator(start_date, end_date)

def logs_creation(missing_days=None, 
                  launcher=None, 
                  seller_ids_list=None, 
                  execution_time=None,
                  saved_records=None, 
                  logs_type:list=['launched', 'outputs']):
    if logs_type == 'launched':
        current_time = datetime.now()
        launched_day = datetime.strftime(current_time, '%Y-%m-%d %H:%M:%S')
        records_count = len(seller_ids_list) * len(missing_days)
        launched_logs = f"""
------------------Launched Logs------------------
Launched Jobs For: ```ml\nScrape Lazada Brand Portal```
Environment: Production
Launcher: {launcher}
Records count: {records_count}
Launched at: {launched_day}
        """
        return launched_logs
    elif logs_type == 'outputs':
        output_logs = f"""
------------------Output Logs------------------
Just Finished: ```ml\nScrape Lazada Brand Portal```
Environment: Production
Duration: {execution_time:.4f}
Launcher: {launcher}
Records saved: {saved_records}
        """
        return output_logs
    
def send_message(client_message):
    client = create_discord_client(client_message)
    try:
        loop = asyncio.get_running_loop()
    except Exception:
        asyncio.run(run_discord_client(client))
    else:
        loop.create_task(run_discord_client(client))

with sync_playwright() as pw: 
    main_df = pd.DataFrame()
    start_time = time.time()
    #Print the message to start the job
    launched_logs = logs_creation(missing_days=missing_days, launcher=launcher, \
                                  seller_ids_list=seller_ids_list,logs_type='launched')
    send_message(launched_logs)

    print('Start connecting to web browser')
    browser = pw.chromium.connect_over_cdp(debugging_url)
    context = browser.contexts[0]
    page = context.pages[0]
    print(f'Connected to page {page}')
    
    print('Start downloading files')
    for seller in working_list: 
        home_decision = random.randint(0, 1)

        #Navigate to the product section
        getting_product = page.wait_for_selector('span.ant-menu-title-content a.MOSRIN')
        if getting_product: 
            a_elements = page.query_selector_all('span.ant-menu-title-content a.MOSRIN')
            for a in a_elements: 
                if 'product' in a.text_content().lower(): 
                    a.click() 

        #Navigate to the all stores section
        getting_store = page.wait_for_selector('div.CQQLcL.v6BP9E')
        if getting_store: 
            getting_store.click()
            time.sleep(1)

        #Check for the select all sections
        select_all_check = page.query_selector('div.ZKwJZ5 div span.my-checkbox.css-gkqwjw.my-checkbox-checked')
        if select_all_check is None: 
            select_all_button = page.query_selector('div.ZKwJZ5 div span')
            if select_all_button: 
                select_all_button.click()
                time.sleep(0.5)

        #Defining the selected countries
        getting_countries = page.wait_for_selector('ul.my-cascader-menu') 
        input_country = getting_country(seller.get('seller_id', ''))
        if getting_countries:   
            all_countries = page.query_selector_all('ul.my-cascader-menu')[0]
            if all_countries: 
                li_items = all_countries.query_selector_all('li')
                for li in li_items: 
                    if input_country == li.text_content().lower() or input_country == li.text_content(): 
                        selected_country = li.query_selector('div')
                        print(f'Selected country is {li.text_content()}')
                        print(f'Start working with seller {seller}')
                    else: 
                        span_elements = li.query_selector_all('span')[0]
                        if span_elements: 
                            span_elements.click()
                            # random_sleep = random.randint(0, 5)
                            # time.sleep(random_sleep)                         
        
        #Refocusing on the country element 
        selected_country.hover()

        #Getting the appropripate channels
        getting_channels = page.wait_for_selector('ul.my-cascader-menu') 
        input_seller_type = seller.get('seller_type', '')
        if getting_channels:   
            all_channels = page.query_selector_all('ul.my-cascader-menu')[1]
            if all_channels: 
                li_items = all_channels.query_selector_all('li')
                for li in li_items: 
                    similar_ratio = fuzz.ratio(li.text_content().lower(), input_seller_type.lower())
                    if similar_ratio > 80: 
                       selected_channel = li
                    else:
                        span_elements = li.query_selector_all('span')[0]
                        if span_elements: 
                            span_elements.click()
                            # random_sleep = random.randint(0, 5)
                            # time.sleep(random_sleep)                  
        
        #Refocus on the selected country
        selected_channel.hover()

        #Getting the appropriate seller name
        getting_seller_name = page.wait_for_selector('ul.my-cascader-menu') 
        input_seller_name = seller.get('seller_name', '')
        if getting_seller_name:   
            all_seller_names = page.query_selector_all('ul.my-cascader-menu')[2]
            if all_seller_names: 
                li_items = all_seller_names.query_selector_all('li')
                for li in li_items: 
                    # count = 0
                    # brand_portal_word = li.text_content().lower().split(' ')
                    # seller_name_word = input_seller_name.lower().split(' ')
                    # for word in seller_name_word: 
                    #     if word in brand_portal_word: 
                    #         count += 1
                    # if count >= len(seller_name_word): 
                    #     selected_seller_name = li
                    brand_portal_word = li.text_content().lower()
                    seller_name_word = input_seller_name.lower()
                    if brand_portal_word == seller_name_word: 
                        selected_seller_name = li
                    else: 
                        span_elements = li.query_selector_all('span')[0]
                        if span_elements: 
                            span_elements.click()
                            # random_sleep = random.randint(0, 5)
                            # time.sleep(random_sleep) 
        printed_flagged = False
        while True: 
            total_buttons = box_validations(page)
            if total_buttons == 3:
                break 
            else: 
                placeholders = page.query_selector('div.my-select-dropdown.bl_ZY8.my-cascader-dropdown.css-gkqwjw.my-select-dropdown-placement-bottomLeft')
                placeholders.hover() 
                if printed_flagged == False: 
                    print(f'Clicked not expected at {total_buttons} buttons')
                    print(f'Failed clicking for seller {seller}') 
                    printed_flagged = True

        #Pressing the confirm button 
        confirm_button = page.wait_for_selector('button.my-btn.css-gkqwjw.my-btn-primary')
        if confirm_button: 
            confirm_button.click()
            time.sleep(1)
        
        #Start working with download the files
        print(f'Start downloading files for seller {seller.get('seller_id')}')
        for missing_day in missing_days: 
            day_button = page.query_selector('button.ant-btn.css-18w61nb.ant-btn-primary.ant-btn-sm')
            calendar_object = hovering_date(day_button, page)
            if calendar_object: 
                month_year_object = page.query_selector('div.oui-dt-calendar-content.day')
                current_year = month_year_object.query_selector('span[data-role="current-year"]').text_content()
                current_month = month_year_object.query_selector('span[data-role="current-month"]').text_content()
                date_string = f'{current_year}-{current_month}'
                calendar_day_object = getting_calendar_year_month(date_string)
                missing_day_object = datetime.strptime(missing_day[:8] + '01', '%Y-%m-%d')
                while True:
                    #When missing days lower than the calendar day, go backward
                    if missing_day_object < calendar_day_object:
                        previous_button = page.query_selector('span.oui-dt-calendar-control[data-role="prev-month"]')
                        previous_button.click()
                        time.sleep(1)
                        month_year_object = page.wait_for_selector('div.oui-dt-calendar-content.day')
                        current_year = month_year_object.query_selector('span[data-role="current-year"]').text_content()
                        current_month = month_year_object.query_selector('span[data-role="current-month"]').text_content()
                        date_string = f'{current_year}-{current_month}'
                        calendar_day_object = getting_calendar_year_month(date_string)
                    #When missing days lower than the calendar day, go forward
                    elif missing_day_object > calendar_day_object: 
                        next_button = page.query_selector('span.oui-dt-calendar-control[data-role="next-month"]')
                        next_button.click()
                        time.sleep(1)
                        month_year_object = page.wait_for_selector('div.oui-dt-calendar-content.day')
                        current_year = month_year_object.query_selector('span[data-role="current-year"]').text_content()
                        current_month = month_year_object.query_selector('span[data-role="current-month"]').text_content()
                        date_string = f'{current_year}-{current_month}'
                        calendar_day_object = getting_calendar_year_month(date_string)
                    #When finds the match day, then break
                    elif missing_day_object == calendar_day_object: 
                        break
            
            #Getitng all the days
            all_rows_days = page.query_selector_all('tbody tr.oui-dt-calendar-date-column')
            date_object = datetime.strptime(missing_day, '%Y-%m-%d')
            for single_row in all_rows_days: 
                all_days_in_row = single_row.query_selector_all('td.current-month')
                for single_day in all_days_in_row: 
                    if single_day.text_content() == str(date_object.day): 
                        single_day.click() 
                        break                  
            #Getting the export button 
            with page.expect_download() as download_info: 
                export_button = page.query_selector('div.v4dEWt a')
                if export_button: 
                    export_button.click()
            download = download_info.value
            current_time = datetime.now()
            current_time = datetime.strftime(current_time, '%Y-%m-%d')
            seller_id = seller.get('seller_id')
            file_name = f'{seller_id}_{missing_day}_brand-portal-download_{launcher}_{current_time}.xls'
            download_path = os.path.join(download_dir, file_name)
            download.save_as(download_path)
            if len(main_df) == 0:
                main_df = pd.read_excel(download_path, skiprows=5)
                main_df['Day'] = missing_day
            else: 
                bp_df = pd.read_excel(download_path, skiprows=5)
                bp_df['Day'] = missing_day
                main_df = pd.concat([main_df, bp_df], ignore_index=True)
            try: 
                upload_to_folder(download_path, file_name)
            except Exception as e:
                print(f"Error processing file: {e}")
            
            #Saved the full df to the database
            random_int = random.randint(1, 4)
            time.sleep(0.1)

        #Decide to navigate back home or not
        if home_decision == 0: 
            getting_home = page.wait_for_selector('span.ant-menu-title-content a.MOSRIN')
            if getting_home:
                a_elements = page.query_selector_all('span.ant-menu-title-content a.MOSRIN')
                for a in a_elements: 
                    if 'home' in a.text_content().lower(): 
                        a.click() 
                        time.sleep(2)

print('Start saving the data')
save_to_database(main_df)
end_time = time.time()
execution_time = end_time - start_time
#Print the logs to finish the job
output_logs = logs_creation(launcher=launcher, execution_time=execution_time, 
    saved_records=len(main_df), logs_type='outputs')
send_message(output_logs)
sys.exit()
            
                        
        
