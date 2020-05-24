from PIL import Image

base = Image.open("./images/Policy_Base.png")
print(base.size)

bcard = Image.open("./images/Policy_Liberal.png")
rcard = Image.open("./images/Policy_Fascist.png")
print(bcard.size)

new = base.copy()
new.paste(rcard, (120, 117), rcard)
new.paste(rcard, (360, 117), rcard)
new.show()
