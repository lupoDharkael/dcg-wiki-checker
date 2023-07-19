#!/usr/bin/env python3

import requests
import wikitextparser as wtp
import time
import sys
import json
import os


CARD_TEMPLATE = "https://digimoncardgame.fandom.com/api.php?action=parse&page={0}&prop=wikitext&format=json"

SLEEP_TIME = 0.20

MAX_PLAYCOST = 25


page_templates = ['ST1-{:02d}', 'ST2-{:02d}', 'ST3-{:02d}', 'ST4-{:02d}', 'ST5-{:02d}', 'ST6-{:02d}',
    'ST7-{:02d}', 'ST8-{:02d}', 'ST9-{:02d}', 'ST10-{:02d}', 'ST12-{:02d}', 'ST13-{:02d}', 'P-{:03d}', 'BT1-{:03d}', 'BT2-{:03d}',
    'BT3-{:03d}', 'BT4-{:03d}', 'BT5-{:03d}', 'BT6-{:03d}', 'EX1-{:03d}', 'BT7-{:03d}', 'BT8-{:03d}',
    'EX2-{:03d}', 'BT9-{:03d}', 'BT10-{:03d}',
    'EX3-{:03d}', 'BT11-{:03d}', 'BT12-{:03d}', 'EX4-{:03d}', 'BT13-{:03d}', 'ST15-{:02d}', 'ST16-{:02d}', 'BT14-{:03d}', 'LM1-{:02d}']

series_name_list = ["ST-1: Gaia Red", "ST-2: Cocytus Blue", "ST-3: Heaven's Yellow",
    "ST-4: Giga Green", "ST-5: Mugen Black", "ST-6: Venomous Violet", "ST-7: Gallantmon",
    "ST-8: UlforceVeedramon", "ST-9: Ultimate Ancient Dragon", "ST-10: Parallel World Tactician",
    "ST-12: Starter Deck Jesmon", "ST-13: Starter Deck RagnaLoardmon", "Promo: Promotional Cards", "BT-01: New Evolution", "BT-02: Ultimate Power", "BT-03: Union Impact", "BT-04: Great Legend", "BT-05: Battle of Omega", "BT-06: Double Diamond", "EX-01: Classic Collection", "BT-07: Next Aventure", "BT-08: New Hero", "EX-02: Digital Hazard", "BT-09: X Record", "BT-10: Xros Encounter", "EX-03: Draconic Roar", "BT-11: Dimensional Phase", "BT-12: Across Time", "EX-04: Alternative Being", "BT-13: Against Royal Knights", "ST-15: Dragon of Courage", "ST-16: Wolf of Friendship", "BT-14: Blast Ace", "LM-01: Digimon Ghost Game"]


report_res = []

def report_err(id, name, err):
    err_msg = id + ' ' + name + ': ' + err + '.'
    print(err_msg)
    report_res.append(err_msg)


def print_report():
    print("---------------")
    print("Report summary:")
    for e in report_res:
        print(e)


class CollectionChecker(object):
    _last_level = "3"
    _last_cost = 0
    _last_card_type = ""

    _session = None

    def __init__(self, session):
                self._session = session

    def check_card_wikitext(self, card_wikitext, page_id) -> dict:
        card_data = {}

        # Card data
        card_wikitext = card_wikitext.replace('\n', '').replace(' = ', '=')
        parsed_data = wtp.parse(card_wikitext)

        for template in parsed_data.templates:
            if template.name == 'CardTable':
                for argument in template.arguments:
                    arg_name = argument.name.strip()
                    arg_value = argument.value.strip()
                    if not arg_value:
                        continue
                    card_data[arg_name] = arg_value

        if card_data['cardtype'] != self._last_card_type:
            self._last_level = "2"
            self._last_cost = 0
        # DIGITAMA CHECKS
        if card_data['cardtype'] == 'Digi-Egg':
            # LEVEL
            if card_data['level'] != '2':
                report_err(page_id, card_data['name'], '"cardtype" defined as "Digi-Egg" but its "level" is not 2')
            # TYPE
            if 'type' not in card_data:
                report_err(page_id, card_data['name'], '"type" not defined')
        # DIGIMON CHECKS
        elif card_data['cardtype'] == 'Digimon':
            # LEVEL
            if 'level' not in card_data:
                report_err(page_id, card_data['name'], '"level" not defined')
            elif not card_data['level'].isnumeric():
                report_err(page_id, card_data['name'], '"level" is not a number')
            elif card_data['level'] < self._last_level:
                report_err(page_id, card_data['name'], '"level" = ' + card_data['level'] + ' and previous digimon card had level ' + self._last_level)
            elif card_data['type'] =='In-Training':
                report_err(page_id, card_data['name'], 'has "In-Training" in its form')
            else:
                self._last_level = card_data['level']
            # PLAYCOST
            if 'playcost' not in card_data:
                report_err(page_id, card_data['name'], '"playcost" not defined')
            elif not card_data['playcost'].isnumeric():
                report_err(page_id, card_data['name'], '"playcost" is not a number')
            elif int(card_data['playcost']) >= MAX_PLAYCOST:
                report_err(page_id, card_data['name'], '"playcost" = ' + card_data['playcost'])
            elif int(card_data['playcost']) < self._last_cost:
                report_err(page_id, card_data['name'], '"playcost" = ' + card_data['playcost'] + ' and previous digimon card had playcost ' + self._last_cost)
            else:
                self._last_cost = int(card_data['playcost'])
            # DP
            if 'dp' not in card_data:
                report_err(page_id, card_data['name'], '"dp" not defined')
            elif not card_data['dp'].isnumeric():
                report_err(page_id, card_data['name'], '"dp" is not a number')
            # TYPE
            if 'type' not in card_data:
                report_err(page_id, card_data['name'], '"type" not defined')
        # TAMER CHECKS
        elif card_data['cardtype'] == 'Tamer':
            # PLAYCOST
            if 'playcost' not in card_data:
                report_err(page_id, card_data['name'], '"playcost" not defined')
            elif not card_data['playcost'].isnumeric():
                report_err(page_id, card_data['name'], '"playcost" is not a number')
            elif int(card_data['playcost']) >= MAX_PLAYCOST:
                report_err(page_id, card_data['name'], '"playcost" = ' + card_data['playcost'])
            elif int(card_data['playcost']) < self._last_cost:
                report_err(page_id, card_data['name'], '"playcost" = ' + card_data['playcost'] + ' and previous digimon card had playcost ' + self._last_cost)
            else:
                self._last_cost = int(card_data['playcost'])
        # OPTION CHECKS
        else: # Option
            # PLAYCOST
            if 'playcost' not in card_data:
                report_err(page_id, card_data['name'], '"playcost" not defined')
            elif not card_data['playcost'].isnumeric():
                report_err(page_id, card_data['name'], '"playcost" is not a number')
            elif int(card_data['playcost']) >= MAX_PLAYCOST:
                report_err(page_id, card_data['name'], '"playcost" = ' + card_data['playcost'])
            elif int(card_data['playcost']) < self._last_cost:
                report_err(page_id, card_data['name'], '"playcost" = ' + card_data['playcost'] + ' and previous digimon card had playcost ' + self._last_cost)
            else:
                self._last_cost = int(card_data['playcost'])

    def check_collection(self, idx):
        page_template = page_templates[idx]

        page_index = 0
        while True:
            page_index += 1
            if page_index != 1:
                time.sleep(SLEEP_TIME)

            page_id = page_template.format(page_index)

            # Card
            response = self._session.get(CARD_TEMPLATE.format(page_id))
            if response.status_code != 200:
                print("HTTP error")
                sys.exit(1)

            json_response = response.json()
            if 'error' in json_response:
                break
            card_wikitext = json_response['parse']['wikitext']['*']

            print("Checking " + page_id + "...")
            self.check_card_wikitext(card_wikitext, page_id)


def main():
    if len(page_templates) != len(series_name_list):
        print("Error: the page list and series name list differ in length")
        sys.exit(1)

    if len(sys.argv) < 2:
        print("Use the following numbers to choose which sets to check:")
        for idx, name in enumerate(series_name_list):
            print(idx, name)
        print("\nUsage:")
        print("wiki_to_json.py --all")
        print("wiki_to_json.py 1 4 5")

        sys.exit(0)

    booster_indices = []
    if sys.argv[1] == "--all":
        booster_indices = list(range(len(page_templates)))
    else:
        booster_indices = sys.argv[1:]
    #

    session = requests.Session()
    for idx in booster_indices:
        idx = int(idx)
        cc = CollectionChecker(session)
        cc.check_collection(idx)
    print_report()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print('\nCheck Interrupted!')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
