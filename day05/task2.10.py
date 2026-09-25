superheroes = {
    "Batman": {
        "id": 1,
        "aliases": ["Bruce Wayne", "Dark knight"],
        "location": {"number": 1007, "street": "Mountain Drive", "city": "Gotham"},
    },
    "Superman": {
        "id": 2,
        "aliases": ["Kal-El", "Clark Kent", "The Man of Steel"],
        "location": {"number": 344, "street": "Clinton Street",
                     "apartment": "3D", "city": "Metropolis"},
    },
}

superheroes["Batman"]["aliases"].append("Caped Crusader")
superheroes["Wolverine"] = {"id": 3}


for name, info in superheroes.items():
    print(name + ":")
    if "aliases" in info:
        for alias in info["aliases"]:
            print(alias)
    else:
        print("No aliases found.")
    print()