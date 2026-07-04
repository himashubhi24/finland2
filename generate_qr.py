import qrcode

upi_link = "upi://pay?pa=bharatpe.8k0i1d0x6l74683@fbpe&pn=Premium Access&am=15&cu=INR"

img = qrcode.make(upi_link)

img.save("qr.png")

print("QR Generated")
