import html
import requests
from bs4 import BeautifulSoup
import re
import json
from next_api import next_get_shot_json, next_direct_get_shot_json


IMAGE_BASE_URL = "https://xcdn.next.co.uk/COMMON/Items/Default/Default/ItemImages/AltItemZoom/"


def get_product_title(soup):
    try:
        style_header = soup.find('div', class_='StyleHeader')
        title_div = style_header.find('div', class_='Title')
        title = title_div.find('h1').get_text().strip()
        print("PRODUCT_NAME = ", title)
        return title
    except:
        return ""


def get_article_tag_info(article_tag):
    try:
        category = article_tag['data-category']
    except:
        category = ""
    try:
        department = article_tag['data-department']
    except:
        department = ""
    try:
        gender = article_tag['data-gender']
    except:
        gender = ""
    try:
        brand = article_tag['data-brand']
    except:
        brand = ""
    try:
        collection = article_tag['data-collection']
    except:
        collection = ""
    try:
        material = article_tag['data-material']
    except:
        material = ""
    try:
        default_colour = article_tag['data-defaultitemcolour']
    except:
        default_colour = ""
    try:
        seo_product_name = article_tag['seoproductname']
    except:
        seo_product_name = ""

    article_tag_data = {
        'category': category,
        'department': department,
        'gender': gender,
        'brand': brand,
        'collection': collection,
        'material': material,
        'default_colour': default_colour,
        'seo_product_name': seo_product_name,
    }

    return article_tag_data


def control_duplicate(all_list, style_id):
    for product in all_list:
        product_style_id = product['style_id']
        if style_id == product_style_id:
            print("TEKRAR EDİLEN ÜRÜN !", style_id)
            return False
    return True


def get_media(media):
    try:
        photo1 = media[0]['name']
    except:
        photo1 = ""

    try:
        photo2 = media[1]['name']
    except:
        photo2 = ""

    try:
        photo3 = media[2]['name']
    except:
        photo3 = ""

    try:
        photo4 = media[3]['name']
    except:
        photo4 = ""

    return photo1, photo2, photo3, photo4


def get_media_uk(media):
    try:
        photo1 = media[0]['nm']
    except:
        photo1 = ""

    try:
        photo2 = media[1]['nm']
    except:
        photo2 = ""

    try:
        photo3 = media[2]['nm']
    except:
        photo3 = ""

    try:
        photo4 = media[3]['nm']
    except:
        photo4 = ""

    return photo1, photo2, photo3, photo4


def get_coords(page_content):
    pattern = r'new coordsModule\.coords\((.*?)\);'
    matches = re.search(pattern, page_content, re.S)
    if matches:
        json_data = matches.group(1)
        # JSON verisini yükle
        data = json.loads(json_data)
        return data
    else:
        print("JSON verisi bulunamadı.")
        return None


def get_item_numbers(html_content):
    item_numbers = []
    shot_data = get_shot_data(html_content)
    if shot_data is None:
        return None
    else:
        styles = shot_data['Styles'][0]
        fits = styles['Fits']
        for fit in fits:
            items = fit['Items']
            name = fit['Name']
            for item in items:
                item_number = str(item['ItemNumber'])
                item_number = item_number.replace('-', '')
                item_info = {
                    'item_number': item_number,
                    'fit_name': name
                }
                item_numbers.append(item_info)

    return item_numbers


def get_shot_data(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    shot_data_script = soup.find('script', id='shotData')
    if shot_data_script:
        shot_data_match = re.search(r'var\s+shotData\s*=\s*({.*?});', shot_data_script.text, re.DOTALL)
        if shot_data_match:
            # print(shot_data_match)
            shot_data_json = shot_data_match.group(1)
            shot_data_dict = json.loads(shot_data_json)
            # print(shot_data_dict)
            return shot_data_dict
        else:
            print("shot_data bulunamadı")
            return None
    else:
        print("shot_data_script bulunamadı")
        return None


def get_all_variant_detail(styles, style_id, product_id, style_name, main_category, style_code, article_tag_data, product_title):
    base_url = "https://www.nextdirect.com/tr/en/style/"
    fits = styles['Fits']
    tone_of_voice = ""
    default_item_colour = ""
    brand_style = ""
    try:
        tone_of_voice = styles['ToneOfVoice']
        default_item_colour = styles['DefaultItemColour']
        brand_style = styles['Brand']
    except:
        pass
    variants = []
    try:
        for fit in fits:
            fit_name = fit['Name']
            fit_items = fit['Items']
            for item in fit_items:
                item_number = str(item['ItemNumber'])
                item_number = item_number.replace('-', '')
                item_colour = item['Colour']
                item_full_price = item['FullPrice']
                item_composition = item['Composition']
                item_washing_instructions = item['WashingInstructions']
                is_sold_out = item['IsSoldOut']
                web_data = item['WebData']
                if len(web_data) < 1:
                    item_descriptions = ""
                else:
                    item_web_data = web_data[0]
                    item_descriptions = item_web_data['Value']

                search_description = item['SearchDescription']
                item_descriptions = html.unescape(item_descriptions)
                item_range = item['Range']
                item_options = item['Options']
                item_media = item['Media']
                photo1, photo2, photo3, photo4 = get_media(item_media)
                photo1 = photo1.replace('-', '')
                for option in item_options:
                    option_number = option['Number']
                    option_name = option['Name']
                    option_stock = option['StockStatus']
                    option_price = option['Price']
                    try:
                        split_size = option['SplitSizes']
                        option_size = split_size[0]['Value']
                    except:
                        option_size = ""

                    item_info = {
                        'product_id': product_id,
                        'url': base_url+str(style_id)+"/"+str(item_number)+"#"+str(item_number),
                        'product_title': product_title,
                        'style_name': style_name,
                        'style_id': style_id,
                        'style_code': style_code,
                        'item_number': item_number,
                        'item_fit': fit_name,
                        'option_number': option_number,
                        'option_stock': option_stock,
                        'is_sold_out': is_sold_out,
                        'option_name': option_name,
                        'option_size': option_size,
                        'item_colour': item_colour,
                        'default_colour': article_tag_data['default_colour'],
                        'default_item_colour': default_item_colour,
                        'item_full_price': item_full_price,
                        'option_price': option_price,
                        'main_category': main_category,
                        'category': article_tag_data['category'],
                        'department': article_tag_data['department'],
                        'gender': article_tag_data['gender'],
                        'brand': article_tag_data['brand'],
                        'brand2': brand_style,
                        'collection': article_tag_data['collection'],
                        'item_composition': item_composition,
                        'item_washing_instructions': item_washing_instructions,
                        'SearchDescription': search_description,
                        'item_descriptions': item_descriptions,
                        'tone_of_voice': tone_of_voice,
                        'item_range': item_range,
                        'material': article_tag_data['material'],
                        'seo_product_name': article_tag_data['seo_product_name'],
                        'photo1': IMAGE_BASE_URL + photo1 + ".jpg",
                        'photo2': IMAGE_BASE_URL + photo2 + ".jpg",
                        'photo3': IMAGE_BASE_URL + photo3 + ".jpg",
                        'photo4': IMAGE_BASE_URL + photo4 + ".jpg",
                    }

                    variants.append(item_info)
        return variants
    except Exception as e:
        print("get_all_variant_detail hata: ", e)

        return variants


def get_one_variant_detail(styles, tradable_item_number, tradable_item_fit, style_name, main_category, style_id, style_code, product_id, article_tag_data, product_title):
    base_url = "https://www.next.co.uk/style/"
    fits = styles['Fits']
    tone_of_voice = ""
    default_item_colour = ""
    brand_style = ""
    try:
        tone_of_voice = styles['ToneOfVoice']
        default_item_colour = styles['DefaultItemColour']
        brand_style = styles['Brand']
    except:
        pass
    variants = []
    try:
        for fit in fits:
            fit_name = fit['Name']
            if fit_name == tradable_item_fit:
                fit_items = fit['Items']
                for item in fit_items:
                    item_number = str(item['ItemNumber'])
                    item_number = item_number.replace('-', '')
                    if item_number == tradable_item_number:
                        item_colour = item['Colour']
                        item_full_price = item['FullPrice']
                        item_composition = item['Composition']
                        item_washing_instructions = item['WashingInstructions']
                        is_sold_out = item['IsSoldOut']
                        item_web_data = item['WebData'][0]
                        search_description = item['SearchDescription']
                        item_descriptions = item_web_data['Value']
                        item_descriptions = html.unescape(item_descriptions)
                        item_range = item['Range']
                        item_options = item['Options']
                        item_media = item['Media']
                        photo1, photo2, photo3, photo4 = get_media_uk(item_media)
                        photo1 = photo1.replace('-', '')
                        for option in item_options:
                            option_number = option['Number']
                            option_name = option['Name']
                            option_stock = option['StockStatus']
                            option_price = option['Price']
                            try:
                                split_size = option['SplitSizes']
                                option_size = split_size[0]['Value']
                            except:
                                option_size = ""

                            item_info = {
                                'product_id': product_id,
                                'url': base_url+str(style_id)+"/"+str(item_number)+"#"+str(item_number),
                                'product_title': product_title,
                                'style_name': style_name,
                                'style_id': style_id,
                                'style_code': style_code,
                                'item_number': item_number,
                                'item_fit': fit_name,
                                'option_number': option_number,
                                'option_stock': option_stock,
                                'is_sold_out': is_sold_out,
                                'option_name': option_name,
                                'option_size': option_size,
                                'item_colour': item_colour,
                                'default_colour': article_tag_data['default_colour'],
                                'default_item_colour': default_item_colour,
                                'item_full_price': item_full_price,
                                'option_price': option_price,
                                'main_category': main_category,
                                'category': article_tag_data['category'],
                                'department': article_tag_data['department'],
                                'gender': article_tag_data['gender'],
                                'brand': article_tag_data['brand'],
                                'brand2': brand_style,
                                'collection': article_tag_data['collection'],
                                'item_composition': item_composition,
                                'item_washing_instructions': item_washing_instructions,
                                'SearchDescription': search_description,
                                'item_descriptions': item_descriptions,
                                'tone_of_voice': tone_of_voice,
                                'item_range': item_range,
                                'material': article_tag_data['material'],
                                'seo_product_name': article_tag_data['seo_product_name'],
                                'photo1': IMAGE_BASE_URL + photo1 + ".jpg",
                                'photo2': IMAGE_BASE_URL + photo2 + ".jpg",
                                'photo3': IMAGE_BASE_URL + photo3 + ".jpg",
                                'photo4': IMAGE_BASE_URL + photo4 + ".jpg",
                                #
                                # 'product_id': product_id,
                                # 'url': base_url+str(style_id)+"/"+str(item_number)+"#"+str(item_number),
                                # 'product_title': product_title,
                                # 'style_id': style_id,
                                # 'style_code': style_code,
                                # 'item_number': item_number,
                                # 'item_fit': tradable_item_fit,
                                # 'item_colour': item_colour,
                                # 'item_full_price': item_full_price,
                                # 'item_composition': item_composition,
                                # 'item_washing_instructions': item_washing_instructions,
                                # 'is_sold_out': is_sold_out,
                                # 'SearchDescription': search_description,
                                # 'item_descriptions': item_descriptions,
                                # 'tone_of_voice': tone_of_voice,
                                # 'item_range': item_range,
                                # 'option_number': option_number,
                                # 'option_name': option_name,
                                # 'option_stock': option_stock,
                                # 'option_price': option_price,
                                # 'category': article_tag_data['category'],
                                # 'department': article_tag_data['department'],
                                # 'gender': article_tag_data['gender'],
                                # 'brand': article_tag_data['brand'],
                                # 'collection': article_tag_data['collection'],
                                # 'material': article_tag_data['material'],
                                # 'default_colour': article_tag_data['default_colour'],
                                # 'seo_product_name': article_tag_data['seo_product_name'],
                                # 'photo1': IMAGE_BASE_URL + photo1 + ".jpg",
                                # 'photo2': IMAGE_BASE_URL + photo2 + ".jpg",
                                # 'photo3': IMAGE_BASE_URL + photo3 + ".jpg",
                                # 'photo4': IMAGE_BASE_URL + photo4 + ".jpg",
                                # 'default_item_colour': default_item_colour,
                                # 'brand2': brand_style,
                                # 'option_size': option_size
                            }
                            variants.append(item_info)
                    else:
                        continue
            else:
                continue

        return variants
    except Exception as e:
        print("get_one_variant_detail hatasi: ", e)


def product_details(base_url, product_id, main_style_id, main_category, all_list):
    all_product_list = []
    url = base_url
    try:
        response = requests.get(url, timeout=20)
    except Exception as e:
        print("RESPONSE ERROR: ",e)
        return None

    print("RESPONSE URL : ", response.url)

    # try:
    if response.status_code == 200:
        article_status = True
        article_tag_data = None
        html_text = response.text
        soup = BeautifulSoup(response.content, 'html.parser')
        product_title = get_product_title(soup)
        coords_data = get_coords(html_text)
        if coords_data is None:
            if "nextdirect" in base_url:
                duplicate = control_duplicate(all_list, main_style_id)
                if not duplicate:
                    return None
                shot_json = next_direct_get_shot_json(main_style_id)
                if shot_json is None:
                    return None
                styles = shot_json['Styles'][0]
                style_code = styles['StyleID']
                style = "Style" + str(style_code)
                # print(style)
                article_tag = soup.find('article', id=style)
                article_tag_data = get_article_tag_info(article_tag)
                variants = get_all_variant_detail(styles, main_style_id, product_id, " ", main_category, style_code, article_tag_data, product_title)
                all_product_list.extend(variants)

            else:
                item_numbers = get_item_numbers(html_content=response.content)
                # print("item_number = ", item_numbers)
                if item_numbers is None:
                    return None
                for item_info in item_numbers:
                    item_number = item_info['item_number']
                    fit_name = item_info['fit_name']
                    duplicate = control_duplicate(all_list, main_style_id)
                    if not duplicate:
                        return None
                    shot_json = next_get_shot_json(main_style_id, item_number)
                    # print(type(shot_json))
                    if shot_json is None:
                        return None
                    else:
                        styles = shot_json['Styles'][0]
                        style_code = styles['StyleID']
                        style = "Style" + str(style_code)
                        # print(style)
                        article_tag = soup.find('article', id=style)
                        article_tag_info = get_article_tag_info(article_tag)
                        variants = get_one_variant_detail(styles, item_number, fit_name, " ", main_category, main_style_id, style_code, product_id, article_tag_info, product_title)
                        all_product_list.extend(variants)
        else:
            try:
                coords_tabs = coords_data['CoordsTabs']
            except:
                return None

            for coords_tab in coords_tabs:
                style_name = coords_tab['Name']
                style_id = coords_tab['StyleId']
                # print("style_id: ", style_id, " - main_Style_id: ", main_style_id)
                duplicate = control_duplicate(all_list, style_id)
                if not duplicate:
                    return None
                if "nextdirect" in base_url:
                    shot_json = next_direct_get_shot_json(style_id)
                    if shot_json is None:
                        continue
                    styles = shot_json['Styles'][0]
                    style_code = styles['StyleID']
                    # print("style_id: ", style_code, " - main_Style_id: ", main_style_id)
                    style = "Style" + str(style_code)
                    # print(style)
                    if article_status:
                        article_status = False
                        article_tag = soup.find('article', id=style)
                        article_tag_data = get_article_tag_info(article_tag)

                    variants = get_all_variant_detail(styles, style_id, product_id, style_name, main_category, style_code, article_tag_data, product_title)
                    # print("variants")
                    # print(variants)
                    all_product_list.extend(variants)

                else:
                    tradable_items = coords_tab['TradableItems']
                    # print("tradable_items: ", tradable_items)
                    for item in tradable_items:
                        tradable_item_number = item['ItemNumber']
                        # tradable_item_Colour = item['Colour']
                        tradable_item_fit = item['Fit']

                        shot_json = next_get_shot_json(style_id, tradable_item_number)
                        # print(type(shot_json))

                        if shot_json is None:
                            continue

                        else:
                            styles = shot_json['Styles'][0]
                            style_code = styles['StyleID']
                            style = "Style" + str(style_id)
                            # print("style_id: ", style_id, " - main_Style_id: ", main_style_id)
                            # print(style)

                            if article_status:
                                article_status = False
                                article_tag = soup.find('article', id=style)
                                article_tag_data = get_article_tag_info(article_tag)
                            variants = get_one_variant_detail(styles, tradable_item_number, tradable_item_fit, style_name, main_category, style_id, style_code, product_id,  article_tag_data, product_title)

                            all_product_list.extend(variants)
        return all_product_list
    else:
        print('REQUEST HATASI')
        return None
    # except Exception as e:
    #     print("HATA: ", e)
    #     return None

# varia , all_i= product_details("https://www.next.co.uk/style/su232009/813029#813029", 1, "ls152144", [])
# print(len(varia))
# print(varia)