import nltk
import string

def clean_cell(cell_string):
    cleaned_cell_string = ''
    for char in cell_string:
        if char != '"':
            cleaned_cell_string += char
    cleaned_cell_string = cleaned_cell_string.strip()
    return cleaned_cell_string

def extract_set_num(field_content):
    if "#281-" not in field_content:
        return "N/A"
    else:
        index = field_content.rfind("#281-")
        set_num = field_content[(index + 5):(index + 7)]
        return set_num

def extract_date_and_time(field_content):
        index = field_content.rfind('BR: "')
        date_and_time = clean_cell(field_content[(index + 3):-1])
        return date_and_time

def systematize_date(date):
    months = {"AUG": '08', "SEP": "09", "OCT": "10", "NOV": "11", "DEC": "12", "JAN": "01"}
    tokens = nltk.word_tokenize(date)
    if "-" in date:
        for word in tokens:
            if "-" in word:
                month = word[:-3]
                if len(month) == 1:
                    month = "0" + month
                year = word[-2:]
                new_string = "19" + year + "-" + month
                return new_string
    else:
        month_text = date[:3].upper()
        month = months[month_text]
        for word in tokens:
            if word[0] in string.digits and ":" not in word:
                day = word
                if len(day) == 1:
                    day = "0" + day
                break
        if "AM" in date:
            am_or_pm = "AM"
        else:
            am_or_pm = "PM"
        if ":" in date:
            for word in tokens:
                if ":" in word:
                    time = word
                    if len(time) == 4:
                        time = "0" + time
                    time = "-" + time
        else:
            time = ""
        new_string = "1940-{}-{}-{}{}".format(month, day, am_or_pm, time)
        return new_string

def create_negative_row(last_row):
    negative_row = last_row[2].append("0").append("1") + last_row[5:]
    return negative_row

file_name = "Citizen_Kane_Continuity_Photos_2018_metadata.csv"
file_open = open(file_name, "r")
rows = file_open.readlines()
file_open.close()

rows_as_lists = []
for row in rows:
    row_as_list = row.split(",")
    rows_as_lists.append(row_as_list)

headers = rows_as_lists[0]
image_data = rows_as_lists[1:]

# Creating Date and Time column
index = -1
for row in image_data:
    index += 1
    field_content = row[headers.index("Annotation - Back")]
    if "BR:" not in field_content:
        date_and_time_standard = "N/A"
    else:
        date_and_time = extract_date_and_time(row[headers.index("Annotation - Back")])
        date_and_time_standard = systematize_date(date_and_time)
    image_data[index] = [date_and_time_standard] + row
headers = ["Date and Time"] + headers

# Creating Set Number column
index = -1
for row in image_data:
    index += 1
    field_content = row[headers.index("Annotation - Front")]
    set_num = extract_set_num(row[headers.index("Annotation - Front")])
    image_data[index] = [set_num] + row
headers = ["Set Number"] + headers

rows_sorted_by_date = sorted(image_data, key=lambda x: x[headers.index("Date and Time")])
rows_sorted_by_set_and_date = sorted(rows_sorted_by_date, key= lambda x: x[headers.index("Set Number")])

# Creating Unique Identifier column
photo_num = 0
index = -1
last_row_set_value = "first"
last_row = []
last_unique_identifier = ""
for row in rows_sorted_by_set_and_date:
    index += 1
    if row[0] != last_row_set_value and last_row_set_value != "first":
        photo_num = 0
    if row[headers.index("Prints (#)")] == '0':
        unique_identifier = "TBD"
    else:
        photo_num += 1
        unique_identifier = "{}-{}-P".format(row[0], photo_num)
    rows_sorted_by_set_and_date[index] = [unique_identifier] + row
    last_row_set_value = row[0]
headers = ["Unique Identifier"] + headers

final_rows = []
tbd_rows = []
for row in rows_sorted_by_set_and_date:
    if row[headers.index("Unique Identifier")] == "TBD":
        tbd_rows.append(row)
    else:
        final_rows.append(row)
final_rows += tbd_rows

final_rows_with_negs = []
for row in final_rows:
    if row[headers.index("Faces (#)")] == "3":
        new_print_row = row[:]
        new_print_row[headers.index("Faces (#)")] = "2"
        new_print_row[headers.index("Negatives (#)")] = "0"
        final_rows_with_negs += [new_print_row]

        neg_row = row[:]
        neg_unique_identifier = row[0][:-1] + "N"
        neg_row[0] = neg_unique_identifier
        neg_row[headers.index("Faces (#)")] = "1"
        neg_row[headers.index("Prints (#)")] = "0"
        final_rows_with_negs += [neg_row]
    else:
        final_rows_with_negs += [row]

# Writing new file
new_file = open("Citizen_Kane_Continuity_Photos_2018_metadata_extra.csv", "w")
new_file.write(",".join(headers))
for row in final_rows_with_negs:
    new_file.write(",".join(row))
new_file.close()
