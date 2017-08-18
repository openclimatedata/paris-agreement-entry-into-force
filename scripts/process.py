# encoding: UTF-8

import os
import sys

from countrynames import to_alpha_3
from datetime import datetime

import pandas as pd

path = os.path.dirname(os.path.realpath(__file__))
treaty_collection_url = ("https://treaties.un.org/Pages/" +
                         "showDetails.aspx?objid=0800000280458f37")
tabula_csv = os.path.join(path, "../archive/tabula-table.csv")
outfile = os.path.join(path, "../data/paris-agreement-entry-into-force.csv")

# Ratification and Signature status from the UN treaty collection.
try:
    tables = pd.read_html(treaty_collection_url, encoding="UTF-8")
except ValueError as e:
    print(e)
    print("Maybe https://treaties.un.org/Pages/ViewDetails.aspx?src=TREATY"
          "&mtdsg_no=XXVII-7-d&chapter=27&clang=_en is down?")
    sys.exit()

status = tables[6]
status.columns = status.loc[0]
status = status.reindex(status.index.drop(0))

status.index = status.Participant.apply(to_alpha_3, fuzzy=True)
status.index.name = "Code"

names = status.Participant.drop_duplicates()
status = status[status.Action.isin(
    ["Ratification", "Acceptance", "Approval", "Signature"])]

signature = status.loc[status.Action == "Signature"]
signature = signature.rename(columns={
    "Date of Notification/Deposit": "Signature"
})
signature = pd.DataFrame(signature.Signature)

ratification = status.loc[status.Action != "Signature"]
ratification = ratification.rename(columns={
    "Action": "Kind",
    "Date of Notification/Deposit": "Ratification-Acceptance-Approval",
    "Date of Effect": "Date-Of-Effect"
    })

status = ratification.join(signature, how="outer")
status["Name"] = names

status = status[["Name", "Signature", "Ratification-Acceptance-Approval",
                 "Kind", "Date-Of-Effect"]]
status.Signature = pd.to_datetime(status.Signature, dayfirst=True)
status["Ratification-Acceptance-Approval"] = pd.to_datetime(
    status["Ratification-Acceptance-Approval"], dayfirst=True)
status["Date-Of-Effect"] = pd.to_datetime(
    status["Date-Of-Effect"], dayfirst=True)

# Add Entry Into Force date for first ratification parties.
status.loc[status["Ratification-Acceptance-Approval"].notnull() &
           status["Date-Of-Effect"].isnull(),
           "Date-Of-Effect"] = datetime(2016, 11, 4)


# Emissions and shares for each country.
# The tabula-table.csv file was generated using Tabula
# (http://tabula.technology/).

def make_int(field):
    try:
        return int(field.replace(" ", ""))
    except ValueError:
        if field == "n/a" or "n/a ":
            return pd.np.NaN
        else:
            return field


# Header rows have been split: "Emissions Gg CO₂ equivalent""
emissions = pd.read_csv(
    "archive/tabula-table.csv",
    index_col=0,
    na_values=["n/a ", "n/a"],
    skiprows=0,
    header=1,
    converters={u'equivalent) ': make_int}
)
emissions.columns = [c.strip() for c in emissions.columns]
emissions.index = [c.strip() for c in emissions.index]
emissions = emissions.rename(columns={"equivalent)": "Emissions"})

# Fix country names that were printed on two lines.
emissions = emissions.rename(index={
    "Bolivia (Plurinational State": "Bolivia (Plurinational State of)",
    "Democratic People's Republic": "Democratic People's Republic of Korea",
    "Democratic Republic of the": "Democratic Republic of the Congo",
    "Lao People's Democratic": "Lao People's Democratic Republic",
    "Micronesia (Federated States": "Micronesia (Federated States of)",
    "Saint Vincent and the": "Saint Vincent and the Grenadines",
    "The former Yugoslav": "The former Yugoslav Republic of Macedonia",
    "United Kingdom of Great":
        "United Kingdom of Great Britain and Northern Ireland",
    "Venezuela (Bolivarian": "Venezuela (Bolivarian Republic of)"
})
emissions = emissions.drop([
    "of)",
    "of Korea",
    "Republic",
    "Grenadines",
    "Republic of Macedonia",
    "Britain and Northern Ireland*",
    "Republic of)"
])
# Drop empty remaining Congo column of "Democratic Republic of the Congo".
emissions = emissions[~emissions.index.duplicated()]

rename_eu_countries = {i: i[:-1] for i in emissions.index if i.endswith("*")}
assert(len(rename_eu_countries) == 27)  # UK already fixed above.
emissions = emissions.rename(index=rename_eu_countries)

emissions = emissions.drop("Total")

# Rename Czechia
status.Name = status.Name.replace(
    "Czech Republic", "Czechia")


# Listed in the footnotes of the table for the purpose of Article 21.
emissions.set_value("European Union", "Emissions", 4488404)
emissions.set_value("European Union", "Percentage", 12.10)
emissions.set_value("European Union", "Year", 2013)

emissions["Name"] = emissions.index
emissions.index = [to_alpha_3(item, fuzzy=True) for item in emissions.Name]
emissions.index.name = "Code"

# Names of parties not yet having signed.
missing = pd.DataFrame(emissions.Name[~emissions.index.isin(status.index)])
status = status.append(missing)


export = status.join(emissions.iloc[:, :3], how="outer")
export = export[["Name", "Signature", "Ratification-Acceptance-Approval",
                 "Kind", "Date-Of-Effect", "Emissions", "Percentage", "Year"]]
export = export.sort_values(by="Name")

print("\nData summary:\n")
print("Emissions sum w/o EU28: {:d} GgCO₂-equiv.".format(int(
    export.Emissions.sum() - export.Emissions.loc['EUU'].sum())))
print("Percentage sum: {}".format(
    export.Percentage.sum() - export.loc['EUU'].Percentage))
print("Count signatures: {}".format(export.Signature.count()))
print("Count ratified: {}".format(
    export["Ratification-Acceptance-Approval"].count()))
ratified = export["Ratification-Acceptance-Approval"].notnull()
percentage_sum = (export[ratified].Percentage.sum() -
                  export.loc["EUU"].Percentage)
print("Sum of percentages with ratification w/o EU: {}".format(
    percentage_sum))


def to_int(x):
    if pd.isnull(x):
        return ""
    else:
        return str(int(x))


export.Emissions = export.Emissions.apply(to_int)
export.Year = export.Year.apply(to_int)
export.to_csv(outfile, encoding="UTF-8")
