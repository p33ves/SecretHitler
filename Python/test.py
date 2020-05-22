from PIL import Image

board = Image.open("./images/Board1.png")
print(board.size)

dot = Image.open("./images/Policy_Facist.png")
print(dot.size)

new = board.copy()
new.paste(dot, (894, 456), dot)
new.show()
