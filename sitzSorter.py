import injuryDict as my_dict  # Importiere deine dict.py Datei


def sort_values(column_count, column_name):
    # Konvertiere die Spaltenanzahl in einen String
    strValue = str(column_count)

    # Überprüfe die Kategorie und gebe den entsprechenden Wert zurück

    if column_name == "Kopf_Gesicht":
        return my_dict.Kopf_Gesicht.get(strValue)
    elif column_name == "Hals":
        return my_dict.Hals.get(strValue)
    elif column_name == "Thorax":
        return my_dict.Thorax.get(strValue)
    elif column_name == "Rippen":
        return my_dict.Rippen.get(strValue)
    elif column_name == "Abdomen":
        return my_dict.Abdomen.get(strValue)
    elif column_name == "Becken":
        return my_dict.Becken.get(strValue)
    elif column_name == "Untere Extremitäten":
        return my_dict.Untere_Extremitäten.get(strValue)
    elif column_name == "Obere Extremitäten":
        return my_dict.Obere_Extremitäten.get(strValue)
    elif column_name == "unbekannt":
        return my_dict.unbekannt.get(strValue)
    else:
        return "Kategorie nicht gefunden"
