import requests
from woo import parent_headers
import pandas as pd

condition_dict = {
    1: "Near Mint",
    2: "Lightly Played",
    3: "Moderately Played",
    4: "Heavily Played",
    5: 'Damaged'
}

def gen_variations(card_headers):
    child_headers = {}
    variation_position = 1
    for k,v in card_headers.items():
        child_headers[k] = v
    child_headers['Type'] = 'variation'
    child_headers["Attribute 3 value(s)"] = ""
    child_headers["Attribute 3 name"] = ""
    child_headers["Attribute 4 value(s)"] = ""
    child_headers["Attribute 4 name"] = ""
    for con_num, con_name in condition_dict.items():

        child_headers['Parent'] = card_headers["SKU"]
        child_headers["Position"] = variation_position
        child_headers["Attribute 1 value(s)"] = con_name
        child_headers["Tax class"] = "Parent"
        child_headers["Attribute 2 value(s)"] = "Foil"
        add_dict = {}
        child_headers["SKU"] = card_headers["SKU"] + f"-{con_num}F"
        for key,val in child_headers.items():
            add_dict[key] = [val]
        new_data = pd.DataFrame(data=add_dict)
        new_data.to_csv("./swu-cards.csv", sep=",", index=False, mode="a+", header=None)
        variation_position += 1
        child_headers["Position"] = variation_position
        child_headers["Attribute 2 value(s)"] = "Non Foil"
        add_dict = {}
        child_headers["SKU"] = card_headers["SKU"] + f"-{con_num}NF"
        for key,val in child_headers.items():
            add_dict[key] = [val]
        new_data = pd.DataFrame(data=add_dict)
        new_data.to_csv("./swu-cards.csv", sep=",", index=False, mode="a+", header=None)
        variation_position += 1

def seed_csv():
    dburl = "https://api.swu-db.com/cards/sor"
    response = requests.get(dburl).json()

    for card in response['data']:
        card_parent_headers = {}
        for k, v in parent_headers.items():
            card_parent_headers[k] = v
        card_parent_headers['SKU'] = f'{card["Set"]}-{card["Number"]}'
        card_parent_headers['Name'] = card['Name']
        if 'Subtitle' in card.keys():
            card_parent_headers['Name'] += " - " + card['Subtitle']
        cat_string = ""
        if 'Aspects' in card.keys():
            for aspect in card['Aspects']:
                cat_string += f"Star Wars Unlimited > {card['Type']} > {aspect}"
                if len(cat_string) > 0:
                    cat_string += ","
        else:
            cat_string = f"Star Wars Unlimited > {card['Type']} > None"
        card_parent_headers['Categories'] = cat_string
        card_parent_headers['Tags'] = f"Star Wars"
        if 'Aspects' in card.keys():
            for aspect in card['Aspects']:
                card_parent_headers['Tags'] += f", {aspect}"
        card_parent_headers['Tags'] += f", {card['Type']}"
        if 'Traits' in card.keys():
            for trait in card["Traits"]:
                card_parent_headers['Tags'] += f", {trait}"
        card_parent_headers['Images'] = card['FrontArt']
        if card['DoubleSided']:
            card_parent_headers['Images'] += f", {card['BackArt']}"
        card_parent_headers['Attribute 3 value(s)'] = card['Rarity']
        card_parent_headers['Attribute 4 value(s)'] = card['Type']

                
        
        new_dict = {}
        for k,v in card_parent_headers.items():
            new_dict[k] = [v]
        new_data = pd.DataFrame(data=new_dict)
        new_data.to_csv("./swu-cards.csv", sep=",", index=False, mode='a+', header=None)
        gen_variations(card_parent_headers)




def clear_csv():
    current = pd.read_csv("./swu-cards.csv", sep=",")
    current = current.head(0)
    current.to_csv("./swu-cards.csv", sep=",", index=False)


def add_new_cards():
    while True:
        print("What Card number would you like to add to?")
        card_num = input()
        print("How many would you like to add?")
        ammount = input()
        print("What condition are they in?")
        condition = input()
        print("Foil or Non Foil? (F/NF)")
        foiled = input().upper()
        print(f"We are adding {ammount}x {foiled} {card_num} in {condition_dict[int(condition)]} condition?")
        y_or_n = input()
        if y_or_n.lower() == 'y':
            base_sku = f"SOR-{card_num}"
            sku = f"SOR-{card_num}-{condition}{foiled}"
            current_csv = pd.read_csv("./swu-cards.csv", sep=",")
            current_csv.loc[current_csv["SKU"] == base_sku, "Stock"] += int(ammount)
            current_csv.loc[current_csv["SKU"] == sku, "Stock"] += int(ammount)
            current_csv.to_csv("./swu-cards.csv", sep=",", index=False)
clear_csv()
seed_csv()
add_new_cards()
