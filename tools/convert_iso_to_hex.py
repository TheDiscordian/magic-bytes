string = input("Tell me what to hexify: ")
hex_string = " ".join("{:02X}".format(ord(c)) for c in string)
print(hex_string)