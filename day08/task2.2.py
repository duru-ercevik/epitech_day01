import turtle
toto = turtle.Screen() #assigning the background to toto
toto.bgcolor("black")  #making background black
titi = turtle.Turtle() #assigning the turtle to titi
titi.color("red") #making titi red
for i in range(3):
    titi.right(90) #90 degree to right
    titi.circle(42) #making a square with radius 42 
toto.exitonclick() #it stays open until clicked