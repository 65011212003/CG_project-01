from PIL import Image, ImageDraw
import os

# Create a simple icon
img = Image.new('RGBA', (256, 256), color=(255, 255, 255, 0))
draw = ImageDraw.Draw(img)

# Draw a simple pencil icon
draw.rectangle((50, 50, 206, 206), fill=(0, 120, 215))
draw.polygon([(50, 50), (206, 50), (206, 206), (50, 206)], outline=(0, 0, 0), width=3)
draw.line((80, 80, 176, 176), fill=(255, 255, 255), width=10)
draw.line((176, 80, 80, 176), fill=(255, 255, 255), width=10)

# Save the icon
img.save('app_icon.ico')

print("Icon file created successfully!") 