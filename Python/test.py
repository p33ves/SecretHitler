from PIL import Image

liberalBoard = Image.open("./images/LiberalBoard.png")
liberalBoard = liberalBoard.resize((1080, 360))
# liberalBoard.show()
facistBoard = Image.open("./images/FacistBoard3.png")
facistBoard = facistBoard.resize((1080, 360))
# facistBoard.show()
boardImage = Image.new("RGBA", (1080, 720), "white")
boardImage.paste(liberalBoard, (0, 0, 1080, 360))
boardImage.paste(facistBoard, (0, 360, 1080, 720))
boardImage.show()
