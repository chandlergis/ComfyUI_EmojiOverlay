from PIL import Image, ImageDraw, ImageFont
import torch
import numpy as np
import cairosvg
import io

class ImageEmojiOverlay:
    def __init__(self, device="cpu"):
        self.device = device
    _alignments = ["left", "right", "center"]

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "text": ("STRING", {"multiline": True, "default": "Hello 😊"}),
                "font_size": ("INT", {"default": 16, "min": 1, "max": 256, "step": 1}),
                "x": ("INT", {"default": 0}),
                "y": ("INT", {"default": 0}),
                "font": ("STRING", {"default": "arial.ttf"}),  # Assuming it's a path to a .ttf or .otf file
                "alignment": (cls._alignments, {"default": "left"}),  # ["left", "right", "center"]
                "color": ("INT", {"default": 0, "min": 0, "max": 0xFFFFFF, "step": 1, "display": "color"}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "draw_text_on_image"
    CATEGORY = "image/text"

    def draw_text_on_image(self, image, text, font_size, x, y, font, alignment, color):
        # Convert tensor to numpy array and then to PIL Image
        image_tensor = image
        image_np = image_tensor.cpu().numpy()  # Change from CxHxW to HxWxC for Pillow
        image = Image.fromarray((image_np.squeeze(0) * 255).astype(np.uint8))  # Convert float [0,1] tensor to uint8 image

        # Convert color from INT to RGB tuple
        r = (color >> 16) & 0xFF
        g = (color >> 8) & 0xFF
        b = color & 0xFF
        color_rgb = (r, g, b)

        # Load font
        loaded_font = ImageFont.truetype(font, font_size)

        # Prepare to draw on image
        draw = ImageDraw.Draw(image)

        # Adjust x coordinate based on alignment
        text_width, text_height = draw.textsize(text, font=loaded_font)
        if alignment == "center":
            x -= text_width // 2
        elif alignment == "right":
            x -= text_width

        # Split text into parts to handle emojis separately
        parts = text.split(' ')
        current_x = x

        for part in parts:
            if any(char in part for char in "😊😂❤️👍"):  # Add more emojis as needed
                # Convert emoji to PNG using cairosvg
                svg_data = f'<svg xmlns="http://www.w3.org/2000/svg" width="{font_size}" height="{font_size}"><text y="1em" font-family="{font}" font-size="{font_size}px">{part}</text></svg>'
                png_data = cairosvg.svg2png(bytestring=svg_data)
                emoji_image = Image.open(io.BytesIO(png_data))

                # Paste emoji onto the image
                image.paste(emoji_image, (current_x, y), emoji_image)
                current_x += emoji_image.width
            else:
                # Draw text part
                draw.text((current_x, y), part, fill=color_rgb, font=loaded_font)
                text_width, text_height = draw.textsize(part, font=loaded_font)
                current_x += text_width

        # Convert back to Tensor if needed
        image_tensor_out = torch.tensor(np.array(image).astype(np.float32) / 255.0)  # Convert back to CxHxW
        image_tensor_out = torch.unsqueeze(image_tensor_out, 0)

        return (image_tensor_out,)


NODE_CLASS_MAPPINGS = {
    "Image Emoji Overlay": ImageEmojiOverlay,
}