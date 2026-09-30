import turtle
import random
 
t = turtle.Turtle()
t.speed(0)

turtle.colormode(255)
for i in range(120):
    t.fillcolor(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    t.begin_fill()
    for side in range(4):
        t.forward(200 - i * 1.5)
        t.left(90)
    t.end_fill()
    t.left(10)

turtle.done()
 


