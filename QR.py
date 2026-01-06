import qrcode

# Create an instance of the QRCode class
qr = qrcode.QRCode(
    version=1,  # controls the size of the QR Code
    error_correction=qrcode.constants.ERROR_CORRECT_L,  # controls the error correction used for the QR Code
    box_size=10,  # controls how many pixels each “box” of the QR code is
    border=4,  # controls how many boxes thick the border should be
)

# Set the data for the QR code
url = "https://biomathematicus.me/wp-content/uploads/2025/07/2507.06565v5.pdf"
qr.add_data(url)
qr.make(fit=True)

# Create an Image object from the QR Code instance
img = qr.make_image(fill_color="black", back_color="white")

# Save the image
img.save("QR_arXiv.2507.06565_biomathematicus.png")
