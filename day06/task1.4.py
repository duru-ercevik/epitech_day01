def bread():
    print("<//////////>")
def lettuce():
    print("~~~~~~~~~~~~")
def tomato():
    print("O O O O O O")
def ham():
    print("============")

def make_sandwiches(number, veg=False):
    if type(number) != int or number <= 0:
        print("I can't do this!")
        return
    for i in range(number):
        bread()
        if veg:
            lettuce()
            lettuce()
            tomato()
            tomato()
        else:
            lettuce()
            tomato()
            ham()
            ham()
        bread()
        print()
 
make_sandwiches(1, veg=True)