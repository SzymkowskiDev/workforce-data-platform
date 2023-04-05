import json

# general info
print("Technology name should by writen according to binding standards.")
# user input of technology
tech = input("Enter technology: ")

# open json for read only
with open('fields_and_skills.json', 'r') as f:
    json_object = json.loads(f.read())

# flat list to collect all result from for loop in one line list
flat_list = []

# Git condition - Git is in every field in json file
if tech == 'Git':
    print('Git is important technology in every field.')
# Agile methodology condition - Agile methodology is in every field in json file
elif tech == 'Agile methodology':
    print('Agile methodology is important in every field.')
else:
    # for loop returning fetch all keys having inputted tech in values
    for key, value in json_object.items():
        # finding inputted for every key
        if tech in value:
            # collecting values in flat list
            z = (json_object[key])
            flat_list.append(z)

    # unpacking flat list, which contains other list (values of keys)
    unpacked_list = [element for innerList in flat_list for element in innerList]
    # cleaning duplicated values
    result = []
    [result.append(x) for x in unpacked_list if x not in result]
    # removing inputted technology from results
    if tech in result:
        result.remove(tech)

    # checking if result contains any item, if positive printing result, else printing info
    if len(result) > 0:
        print(result)
    else:
        print('Technology not found.')
