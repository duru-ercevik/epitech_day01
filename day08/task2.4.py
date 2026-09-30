import turtle
 
t = turtle.Turtle()
t.speed(0)
 
for i in range(100):
    t.forward(i * 2)
    t.left(30)
 
turtle.done()