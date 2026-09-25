types = {"Electric": [], "Grass": [], "Fire": []}

types["Electric"].append("Pikachu")
types["Grass"].append("Bulbasaur")
types["Fire"].append("Charmander")
types["Grass"].append("Leafeaon")
types["Grass"].append("Scovillain")
types["Fire"].append("Scovillain")

#first way of doing

for pokemon_type, names in types.items(): #items() gives a key value pair
    if "Pikachu" in names:
        print(pokemon_type)

#second way of doing 

print([t for t in types if "Pikachu" in types[t]])
