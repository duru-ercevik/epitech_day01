import turtle


def draw_polygon(sides):
    t = turtle.Turtle()
    for i in range(sides):
        t.forward(100)
        t.left(360 / sides)

        
draw_polygon(3)
draw_polygon(4)
draw_polygon(6)
turtle.done()