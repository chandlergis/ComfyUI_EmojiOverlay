from PIL import Image, ImageDraw, ImageFont
import torch
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties

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
                "emoji_font": ("STRING", {"default": "/tmp/data/ComfyUI/fonts/NotoColorEmoji-Regular.ttf"}),   # Assuming it's a path to a .ttf or .otf file
                "alignment": (cls._alignments, {"default": "left"}),  # ["left", "right", "center"]
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "draw_text_on_image"
    CATEGORY = "image/text"

    def draw_text_on_image(self, image, text, font_size, x, y, emoji_font, alignment):
        # Convert tensor to numpy array and then to PIL Image
        image_tensor = image
        image_np = image_tensor.cpu().numpy()  # Change from CxHxW to HxWxC for Pillow
        image_pil = Image.fromarray((image_np.squeeze(0) * 255).astype(np.uint8))  # Convert float [0,1] tensor to uint8 image

        # Create a figure and an axes
        dpi = 100
        figsize = (image_pil.width / dpi, image_pil.height / dpi)
        fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
        ax.imshow(image_pil)
        ax.axis('off')  # Hide axes

        # Set the font properties for emoji
        prop = FontProperties(fname=emoji_font, size=font_size)

        # Adjust x coordinate based on alignment
        text_width, text_height = ax.text(0, 0, text, fontproperties=prop).get_window_extent().transformed(fig.dpi_scale_trans.inverted()).width
        if alignment == "center":
            x = (image_pil.width - text_width) / 2
        elif alignment == "right":
            x = image_pil.width - text_width

        # Add text with emoji
        ax.text(x, y, text, fontproperties=prop, verticalalignment='top', horizontalalignment='left')

        # Save to buffer
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0)
        plt.close(fig)
        buf.seek(0)
        img_out = Image.open(buf)

        # Convert back to Tensor if needed
        image_tensor_out = torch.tensor(np.array(img_out).astype(np.float32) / 255.0).permute(2, 0, 1)  # Convert back to CxHxW
        image_tensor_out = torch.unsqueeze(image_tensor_out, 0)

        return (image_tensor,)

NODE_CLASS_MAPPINGS = {
    "Image Emoji Overlay": ImageEmojiOverlay,
}