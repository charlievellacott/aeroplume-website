"""LinkedIn company cover: 1512 x 256, plus a 2x PNG for a sharp upload."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = Path(__file__).resolve().parents[1] / "images"

# Dark navy taken from the plume in the light logo, slightly warmed
# so the cream mark sits on it instead of disappearing into it.
INK = (24, 38, 56)  # #182638
CREAM = (247, 242, 232)  # matches the light logo field
CREAM_SOFT = (214, 206, 193)
COPPER = (210, 138, 96)  # lifted so it reads on dark

SCALE = 6
W, H = 1512 * SCALE, 256 * SCALE


def tracked_width(draw, text, font, tracking):
    width = 0
    for i, ch in enumerate(text):
        width += draw.textlength(ch, font=font)
        if i < len(text) - 1:
            width += tracking
    return width


def draw_tracked(draw, xy, text, font, fill, tracking):
    x, y = xy
    for i, ch in enumerate(text):
        draw.text((x, y), ch, font=font, fill=fill, anchor="ls")
        x += draw.textlength(ch, font=font) + tracking


def rounded_rect_mask(size, radius):
    mask = Image.new("L", size, 0)
    d = ImageDraw.Draw(mask)
    d.rounded_rectangle((0, 0, size[0] - 1, size[1] - 1), radius=radius, fill=255)
    return mask


def render_banner():
    canvas = Image.new("RGB", (W, H), INK)
    draw = ImageDraw.Draw(canvas)

    pala = ImageFont.truetype(r"C:\Windows\Fonts\pala.ttf", 228)
    segoe = ImageFont.truetype(r"C:\Windows\Fonts\segoeui.ttf", 70)
    segoe_url = ImageFont.truetype(r"C:\Windows\Fonts\segoeui.ttf", 66)

    # LinkedIn's page logo covers the lower-left on desktop and mobile.
    # Keep that whole band empty: no second plume, no type.
    text_x = int(W * 0.285)
    mid = H // 2
    line1 = "You do not have to grow up with AI"
    line2 = "to use it well."
    line1_base = mid - 48
    line2_base = mid + 118

    draw.text((text_x, line1_base), line1, font=pala, fill=CREAM, anchor="ls")
    draw.text((text_x, line2_base), line2, font=pala, fill=CREAM, anchor="ls")
    quote_box = draw.textbbox((text_x, line1_base), line1, font=pala, anchor="ls")

    label = "AEROPLUME AI COACHING"
    url = "aeroplume.net"
    tracking = 12
    brand_x = quote_box[2] + 130
    draw_tracked(draw, (brand_x, mid - 28), label, segoe, COPPER, tracking)
    draw.text((brand_x, mid + 72), url, font=segoe_url, fill=CREAM_SOFT, anchor="ls")

    print("text starts at", text_x, f"({text_x / W:.0%} of width)")
    print("quote ends", quote_box[2], "brand starts", brand_x)
    print("brand ends", brand_x + tracked_width(draw, label, segoe, tracking), "canvas", W)

    return canvas


def save_outputs(canvas):
    banner_2x = canvas.resize((1512 * 2, 256 * 2), Image.Resampling.LANCZOS)
    banner = canvas.resize((1512, 256), Image.Resampling.LANCZOS)

    png_2x = ROOT / "linkedin-banner.png"
    png_1x = ROOT / "linkedin-banner-1512.png"
    banner_2x.save(png_2x, "PNG", optimize=True)
    banner.save(png_1x, "PNG", optimize=True)

    # Keep a JPEG copy only as fallback; PNG is the file to upload.
    jpg_2x = ROOT / "linkedin-banner.jpg"
    banner_2x.save(jpg_2x, "JPEG", quality=95, optimize=True, subsampling=0)

    final = canvas.resize((1128, 191), Image.Resampling.LANCZOS)
    final_path = ROOT / "linkedin-banner-final-1128x191.jpg"
    final.save(final_path, "JPEG", quality=95, optimize=True, subsampling=0)

    print("saved", png_2x, png_2x.stat().st_size, banner_2x.size)
    print("saved", png_1x, png_1x.stat().st_size, banner.size)
    print("saved FINAL", final_path, final_path.stat().st_size, final.size)
    return banner_2x


def save_preview(banner_2x):
    """Approximate LinkedIn's logo overlay so we can check clash and crop."""
    scale = 2
    page_w, page_h = 1128 * scale, 420 * scale
    page = Image.new("RGB", (page_w, page_h), (255, 255, 255))

    cover_h = 191 * scale
    cover = banner_2x.resize((page_w, cover_h), Image.Resampling.LANCZOS)
    page.paste(cover, (0, 0))

    logo_src = Image.open(ROOT / "mark-cream.jpg").convert("RGB")
    logo_size = 168 * scale
    logo = logo_src.resize((logo_size, logo_size), Image.Resampling.LANCZOS)
    # Knock the outer field to a clean cream, then round the tile.
    tile = Image.new("RGB", (logo_size, logo_size), (247, 242, 232))
    inset = int(logo_size * 0.18)
    inner = logo.resize((logo_size - inset * 2, logo_size - inset * 2), Image.Resampling.LANCZOS)
    tile.paste(inner, (inset, inset))
    radius = int(logo_size * 0.18)
    mask = rounded_rect_mask((logo_size, logo_size), radius)
    logo_x = 28 * scale
    logo_y = cover_h - int(logo_size * 0.62)
    page.paste(tile, (logo_x, logo_y), mask)

    shadow = Image.new("RGBA", page.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.rounded_rectangle(
        (logo_x + 6, logo_y + 10, logo_x + logo_size + 6, logo_y + logo_size + 10),
        radius=radius,
        fill=(0, 0, 0, 40),
    )
    shadow = shadow.filter(ImageFilter.GaussianBlur(8))
    page = Image.alpha_composite(page.convert("RGBA"), shadow).convert("RGB")
    page.paste(tile, (logo_x, logo_y), mask)

    preview = ROOT / "linkedin-banner-preview.jpg"
    page.save(preview, "JPEG", quality=95, optimize=True)
    print("saved", preview, page.size)


if __name__ == "__main__":
    canvas = render_banner()
    banner_2x = save_outputs(canvas)
    save_preview(banner_2x)
