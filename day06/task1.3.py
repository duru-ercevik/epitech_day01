def bread():
    print("<//////////>")
def lettuce():
    print("~~~~~~~~~~~~")
def tomato():
    print("O O O O O O")
def ham():
    print("============")

def make_sandwiches(number):
    if type(number) != int or number <= 0:
        print("I can't do this!")
        return
    for i in range(number):
        bread()
        lettuce()
        tomato()
        ham()
        ham()
        bread()
        print()
 
make_sandwiches(2)
make_sandwiches(3.14)
