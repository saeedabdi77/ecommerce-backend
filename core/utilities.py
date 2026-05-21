import jdatetime
import uuid

import pandas as pd


def clean_validated_data(model, validated_data):
    """
        get validated_data (dictionary) and model as args
        filter keys that are model fields and returns new dictionary
    """
    new_validated_data = validated_data.copy()
    model_fields = list(map(lambda x: x.name, model._meta.fields))

    for key, value in validated_data.items():
        if key not in model_fields:
            new_validated_data.pop(key)

    return new_validated_data


def empty_value(value):
    return value == '' or value is None


def create_object(model, validated_data):
    """
        get validated_data and model from serializer (create function) and create object
    """
    new_validated_data = clean_validated_data(model, validated_data)
    return model.objects.create(**new_validated_data)


def update_object(instance, validated_data):
    """
        get validated_data and instance from serializer (update function) and update instance
    """
    model = type(instance)
    new_validated_data = clean_validated_data(model, validated_data)

    for attr, value in new_validated_data.items():
        setattr(instance, attr, value)
    instance.save()

    return instance


# arg sample: [{'column1: value1, 'column2: value2}, {'column1: value3, 'column2: value4}, ...]
def dict_to_dataframe(list_of_dicts, columns=None):
    df = pd.DataFrame(list_of_dicts, index=range(1, len(list_of_dicts) + 1))
    if columns and len(list_of_dicts) and len(columns) == len(list_of_dicts[0].keys()):
        df.columns = columns
    return df


def dict_to_excel(list_of_dicts, user, ext='xlsx', columns=None, list_of_dicts_2=None, columns_2=None,
                  sheet_1="sheet_1", sheet_2="sheet_2", file_name_uid=None):
    from core.file_system import FileSystem
    df = dict_to_dataframe(list_of_dicts, columns)
    df_2 = None
    if list_of_dicts_2:
        df_2 = dict_to_dataframe(list_of_dicts_2, columns_2)
    file_name = file_name_uid or str(uuid.uuid4())

    FileSystem.create_temporary_excel_file(df, file_name, user, ext=ext, dataframe_2=df_2, sheet_1=sheet_1,
                                           sheet_2=sheet_2)
    return file_name


def convert_date_to_shamsi(date):
    year, month, day = list(map(lambda x: int(x), str(date).split('-')))

    j = jdatetime.date.fromgregorian(day=day, month=month, year=year).strftime('%Y/%m/%d')

    return j


def gregorian_to_shamsi(date):
    return jdatetime.date.fromgregorian(year=date.year, month=date.month, day=date.day)


persian_ordinal_numbers = {
    1: "اول", 2: "دوم", 3: "سوم", 4: "چهارم", 5: "پنجم", 6: "ششم", 7: "هفتم", 8: "هشتم", 9: "نهم", 10: "دهم",
    11: "یازدهم", 12: "دوازدهم", 13: "سیزدهم", 14: "چهاردهم", 15: "پانزدهم", 16: "شانزدهم", 17: "هفدهم", 18: "هجدهم",
    19: "نوزدهم", 20: "بیستم", 21: "بیست و یکم", 22: "بیست و دوم", 23: "بیست و سوم", 24: "بیست و چهارم",}

def get_persian_ordinal_number(number):
    return persian_ordinal_numbers.get(number)
