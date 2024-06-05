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
                "font": ("STRING", {"default": "/tmp/data/ComfyUI/fonts/Feibo.otf"}),
                "emoji_font": ("STRING", {"default": "/tmp/data/ComfyUI/fonts/NotoColorEmoji-Regular.ttf"}),   # Assuming it's a path to a .ttf or .otf file
                "alignment": (cls._alignments, {"default": "left"}),  # ["left", "right", "center"]
                "color": ("INT", {"default": 0, "min": 0, "max": 0xFFFFFF, "step": 1, "display": "color"}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "draw_text_on_image"
    CATEGORY = "image/text"

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "draw_text_on_image"
    CATEGORY = "image/text"

    def draw_text_on_image(self, image, text, font_size, x, y, font, emoji_font, alignment, color):
        # Convert tensor to numpy array and then to PIL Image
        image_tensor = image
        image_np = image_tensor.cpu().numpy()  # Change from CxHxW to HxWxC for Pillow
        image = Image.fromarray((image_np.squeeze(0) * 255).astype(np.uint8))  # Convert float [0,1] tensor to uint8 image

        # Convert color from INT to RGB tuple
        r = (color >> 16) & 0xFF
        g = (color >> 8) & 0xFF
        b = color & 0xFF
        color_rgb = (r, g, b)

        # Load fonts
        loaded_font = ImageFont.truetype(font, font_size)
        emoji_loaded_font = ImageFont.truetype(emoji_font, font_size)

        # Prepare to draw on image
        draw = ImageDraw.Draw(image)

        # Adjust x coordinate based on alignment
        text_width, text_height = draw.textsize(text, font=loaded_font)
        if alignment == "center":
            x -= text_width // 2
        elif alignment == "right":
            x -= text_width

        # Regular expression to find emoji
        emoji_pattern = re.compile(
            "[\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F680-\U0001F6FF"  # transport & map symbols
            "\U0001F1E0-\U0001F1FF"  # flags (iOS)
            "\U00002702-\U000027B0"  # Dingbats
            "\U000024C2-\U0001F251"
            "]+", flags=re.UNICODE)

        # Split text into parts to handle emojis separately
        parts = emoji_pattern.split(text)
        emojis = emoji_pattern.findall(text)

        current_x = x
        for part, emoji in zip(parts, emojis + [""]):
            # Draw text part
            if part:
                draw.text((current_x, y), part, fill=color_rgb, font=loaded_font)
                text_width, _ = draw.textsize(part, font=loaded_font)
                current_x += text_width

            # Draw emoji part
            if emoji:
                draw.text((current_x, y), emoji, font=emoji_loaded_font)
                emoji_width, _ = draw.textsize(emoji, font=emoji_loaded_font)
                current_x += emoji_width

        # If the text only contains emojis
        if not parts[0] and emojis:
            current_x = x
            for emoji in emojis:
                draw.text((current_x, y), emoji, font=emoji_loaded_font)
                emoji_width, _ = draw.textsize(emoji, font=emoji_loaded_font)
                current_x += emoji_width

        # Convert back to Tensor if needed
        image_tensor_out = torch.tensor(np.array(image).astype(np.float32) / 255.0)  # Convert back to CxHxW
        image_tensor_out = torch.unsqueeze(image_tensor_out, 0)

        return (image_tensor_out,)


NODE_CLASS_MAPPINGS = {
    "Image Emoji Overlay": ImageEmojiOverlay,
}