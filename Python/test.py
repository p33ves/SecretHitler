from PIL import Image

liberalBoard = Image.open("./images/LiberalBoard.png")
print(liberalBoard.size)

facistBoard = Image.open("./images/FacistBoard3.png")
print(facistBoard.size)
""" facistBoard = Image.open("./images/FacistBoard2.png")
print(facistBoard.size)
facistBoard = Image.open("./images/FacistBoard3.png")
print(facistBoard.size) """

liberalBoard = liberalBoard.resize((1110, 364))
# liberalBoard.show()

facistBoard = facistBoard.resize((1110, 364))
# facistBoard.show()
boardImage = Image.new("RGBA", (1110, 728), "white")
boardImage.paste(liberalBoard, (0, 0, 1110, 364))
boardImage.paste(facistBoard, (0, 364, 1110, 728))
boardImage.show()
