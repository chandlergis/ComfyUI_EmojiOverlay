from PIL import Image, ImageDraw, ImageFont
import torch
import numpy as np
import emoji
import io

class ImageEmojiOverlay:
    def __init__(self, device="cpu"):
        self.device = device
        self._alignments = ["left", "right", "center"]

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "text": ("STRING", {"multiline": True, "default": "😊"}),  # Allow emoji characters in the input string
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

        # Render emoji to image
        emoji_image = self.render_emoji(text, font_size)

        # Adjust x coordinate based on alignment
        text_width, text_height = emoji_image.size
        if alignment == "center":
            x -= text_width // 2
        elif alignment == "right":
            x -= text_width

        # Paste emoji image onto the target image
        image.paste(emoji_image, (x, y), emoji_image)

        # Convert back to Tensor if needed
        image_tensor_out = torch.tensor(np.array(image).astype(np.float32) / 255.0)  # Convert back to CxHxW
        image_tensor_out = torch.unsqueeze(image_tensor_out, 0)

        return (image_tensor_out,)

    def render_emoji(self, text, font_size):
        # Create an image with transparent background
        emoji_image = Image.new("RGBA", (font_size, font_size), (255, 255, 255, 0))
        draw = ImageDraw.Draw(emoji_image)

        # Draw emoji on the image
        draw.text((0, 0), text, font=ImageFont.truetype("arial.ttf", font_size), fill=(0, 0, 0, 255))

        return emoji_image

NODE_CLASS_MAPPINGS = {
    "ImageEmojiOverlay": ImageEmojiOverlay,
}