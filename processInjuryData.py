import injuryDict as my_dict  # Importiere deine dict.py Datei
import sitzSorter as my_sorter  # Importiere deine sorter.py Datei

def get_injury_data(column_name, strValue, my_dict):
    column_mapping = {
    "AIS15": my_dict.AIS15,
    "RELI": my_dict.RELI,
    "VORNHINT": my_dict.VORNHINT,
    "PRODI": my_dict.PRODI,
    "INNEN": my_dict.INNEN,
    "FCI15": my_dict.FCI15,
    "MAIS15": my_dict.MAIS15,
    "GESCHL": my_dict.GESCHL,
    "ALTER1": my_dict.ALTER1,
    "ALTER2": my_dict.ALTER2,
    "BEKLST": my_dict.BEKLST,
    "FCI": my_dict.FCI,
    "ISS15": my_dict.ISS15,
    "ART": my_dict.ART,
    "PSKZ": my_dict.PSKZ
    }

    if column_name in column_mapping:
        return column_mapping[column_name].get(strValue)
    else:
        return None  # Or raise an error if the column_name doesn't match any known key

def column_Info(column_value, column_name):

    # Liste zum Speichern der Ergebnisse
    # Extrahiere die erste Ziffer (z.B. 210 -> '2')
    if column_name == "SITZ":
        first_digit = str(column_value)[0]
        category_dict = my_dict.SITZ_kategorien.get(first_digit)
    else:
        category_dict = get_injury_data(
        column_name, str(column_value), my_dict)

    if category_dict is not None:
        strValue = str(column_value)
        if column_name == "SITZ":
            first_digit = str(column_value)[0]
            translation = my_sorter.sort_values(
                column_value, category_dict)
            result_list = {
                "code": strValue,
                "translation": translation,
            }
        else:
            result_list ={
                "code": strValue,
                "translation": category_dict
            }
    else:
        result_list = {

            "code": str(column_value),
            "translation": "Keine Kategorie gefunden"
        }

    return result_list

# print(column_Info(3,'GESCHL'))