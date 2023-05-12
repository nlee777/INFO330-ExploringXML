import sqlite3
import sys
import xml.etree.ElementTree as ET

# Incoming Pokemon MUST be in this format
#
# <pokemon pokedex="" classification="" generation="">
#     <name>...</name>
#     <hp>...</name>
#     <type>...</type>
#     <type>...</type>
#     <attack>...</attack>
#     <defense>...</defense>
#     <speed>...</speed>
#     <sp_attack>...</sp_attack>
#     <sp_defense>...</sp_defense>
#     <height><m>...</m></height>
#     <weight><kg>...</kg></weight>
#     <abilities>
#         <ability />
#     </abilities>
# </pokemon>

# check if XML file name is provided as a command-line argument
if len(sys.argv) < 2:
    print("You must pass at least one XML file name containing Pokemon to insert")
    sys.exit(1)

# connect to the SQLite database
conn = sqlite3.connect("pokemon.sqlite")
cursor = conn.cursor()

# iterate over each XML file name provided
for i, xml_file in enumerate(sys.argv[1:], start=1):
    try:
        # Parse the XML file
        tree = ET.parse(xml_file)
        root = tree.getroot()

        pokedex = root.attrib.get("pokedex", "")
        classification = root.attrib.get("classification", "")
        generation = root.attrib.get("generation", "")
        name = root.find("name").text
        hp = root.find("hp").text
        types = [t.text for t in root.findall("type")]
        attack = root.find("attack").text
        defense = root.find("defense").text
        speed = root.find("speed").text
        sp_attack = root.find("sp_attack").text
        sp_defense = root.find("sp_defense").text
        height = root.find("height_m").text
        weight = root.find("weight_kg").text
        abilities = [a.text for a in root.findall("abilities/ability")]

        query = "SELECT COUNT(*) FROM pokemon WHERE name = ?"
        cursor.execute(query, (name,))
        count = cursor.fetchone()[0]

        if count > 0:
            print(f"Pokemon '{name}' already exists in the database. Skipping insertion.")
            continue

        query = "INSERT INTO pokemon (pokedex, classification, generation, name, hp, attack, defense, speed, sp_attack, sp_defense, height, weight) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
        cursor.execute(query, (pokedex, classification, generation, name, hp, attack, defense, speed, sp_attack, sp_defense, height, weight))
        pokemon_id = cursor.lastrowid

        for type in types:
            query = "INSERT INTO pokemon_types (pokemon_id, type) VALUES (?, ?)"
            cursor.execute(query, (pokemon_id, type))

        for ability in abilities:
            query = "INSERT INTO pokemon_abilities (pokemon_id, ability) VALUES (?, ?)"
            cursor.execute(query, (pokemon_id, ability))

        conn.commit()

        print(f"Pokemon '{name}' inserted successfully
