# DCG Wiki Checker
Sanity checker script for https://digimoncardgame.fandom.com

## Dependencies

```
pip install requests
pip install wikitextparser
```

## How to use

Run the script `check_dcg_wiki.py` and it will show a collumn of numbers associated with each booster, that number is a booster index we can pass as an argument to check that specific booster.

For example `check_dcg_wiki.py 2 20` would check all the cards in `ST-3: Heaven's Yellow` and `BT-07: Next Aventure`.
