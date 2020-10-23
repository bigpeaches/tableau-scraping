import json
import requests
import time


def getTableauViz(url):
    r = requests.get(url, params={":embed": "y", ":showVizHome": "no"})
    return r.text


def getTableauData(scraper):
    dataUrl = f'{scraper.host}{scraper.tableauData["vizql_root"]}/bootstrapSession/sessions/{scraper.tableauData["sessionid"]}'

    r = requests.post(
        dataUrl,
        data={
            "sheet_id": scraper.tableauData["sheetId"],
        },
    )
    scraper.lastActionTime = time.time()
    return r.text


def select(scraper, worksheetName, selection):
    delayExecution(scraper)
    payload = {
        "worksheet": worksheetName,
        "dashboard": scraper.dashboard,
        "selection": json.dumps({"objectIds": selection, "selectionType": "tuples"}),
        "selectOptions": "select-options-simple",
    }
    r = requests.post(
        f'{scraper.host}{scraper.tableauData["vizql_root"]}/sessions/{scraper.tableauData["sessionid"]}/commands/tabdoc/select',
        data=payload,
    )
    return r.json()


def setParameterValue(scraper, parameterName, value):
    delayExecution(scraper)
    payload = (
        ("globalFieldName", (None, parameterName)),
        ("valueString", (None, value)),
        ("useUsLocale", (None, "false")),
    )
    r = requests.post(
        f'{scraper.host}{scraper.tableauData["vizql_root"]}/sessions/{scraper.tableauData["sessionid"]}/commands/tabdoc/set-parameter-value',
        files=payload,
    )
    return r.json()


def delayExecution(scraper):
    if scraper.lastActionTime != 0:
        currentTime = time.time()
        timeDif = currentTime - scraper.lastActionTime
        if timeDif < (scraper.delayMs / 1000):
            waitTime = timeDif + (scraper.delayMs / 1000)
            scraper.logger.debug(f"delaying request by {waitTime} seconds")
            time.sleep(waitTime)
            scraper.lastActionTime = currentTime
        else:
            scraper.lastActionTime = currentTime
