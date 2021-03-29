import sys
import random
from collections import namedtuple
from colorsys import hls_to_rgb
from pathlib import Path
from typing import Optional

from PIL import Image, ImageChops

ProceduralDucky = namedtuple("ProceduralDucky", "image has_hat has_equipment has_outfit")
DuckyColors = namedtuple("DuckyColors", "eye wing body beak")
Color = tuple[int, int, int]

DUCKY_SIZE = (499, 600)
ASSETS_PATH = Path("img/duck-builder")

HAT_CHANCE = .7
EQUIPMENT_CHANCE = .4
OUTFIT_CHANCE = .5


def make_ducky() -> ProceduralDucky:
    return ProceduralDuckyGenerator().generate()


class ProceduralDuckyGenerator:
    templates = {
        int(filename.name[0]): Image.open(filename) for filename in (ASSETS_PATH / "silverduck templates").iterdir()
    }
    hats = [Image.open(filename) for filename in (ASSETS_PATH / "accessories/hats").iterdir()]
    equipments = [Image.open(filename) for filename in (ASSETS_PATH / "accessories/equipment").iterdir()]
    outfits = [Image.open(filename) for filename in (ASSETS_PATH / "accessories/outfits").iterdir()]

    def __init__(self):
        self.output: Image.Image = Image.new("RGBA", DUCKY_SIZE, color=(0, 0, 0, 0))
        self.colors = self.make_colors()

        self.has_hat = False
        self.has_equipment = False
        self.has_outfit = False

    def generate(self) -> ProceduralDucky:
        self.apply_layer(self.templates[5], self.colors.beak)
        self.apply_layer(self.templates[4], self.colors.body)
        self.apply_layer(self.templates[3], self.colors.wing)
        self.apply_layer(self.templates[2], self.colors.eye)
        self.apply_layer(self.templates[1], self.colors.eye)

        if random.random() < HAT_CHANCE:
            self.apply_layer(random.choice(self.hats))
            self.has_hat = True

        if random.random() < EQUIPMENT_CHANCE:
            self.apply_layer(random.choice(self.equipments))
            self.has_equipment = True

        if random.random() < OUTFIT_CHANCE:
            self.apply_layer(random.choice(self.outfits))
            self.has_outfit = True

        return ProceduralDucky(self.output, self.has_hat, self.has_equipment, self.has_outfit)

    def apply_layer(self, layer: Image.Image, recolor: Optional[Color] = None):
        """Add the given layer on top of the ducky. Can be recolored with the recolor argument."""
        if recolor:
            layer = ImageChops.multiply(layer, Image.new("RGBA", DUCKY_SIZE, color=recolor))
        self.output.alpha_composite(layer)

    @staticmethod
    def make_color(hue: float, dark_variant: bool) -> tuple[float, float, float]:
        """Make a nice hls color to use in a duck."""
        saturation = 1
        lightness = random.uniform(.5, .65)
        # green and blue do not like high lightness, so we adjust this depending on how far from blue-green we are
        # hue_fix is the square of the distance between the hue and cyan (0.5 hue)
        hue_fix = (1 - abs(hue - 0.5))**2
        # magic fudge factors
        lightness -= hue_fix * 0.15
        if dark_variant:
            lightness -= hue_fix * 0.25
        saturation -= hue_fix * 0.1

        return hue, lightness, saturation

    @classmethod
    def make_colors(cls) -> DuckyColors:
        """Create a matching DuckyColors object."""
        hue = random.random()
        dark_variant = random.choice([True, False])
        eye, wing, body, beak = (cls.make_color(hue, dark_variant) for i in range(4))

        # Lower the eye light
        eye = (eye[0], min(.9, eye[1] + .4), eye[2])
        # Shift the hue of the beck
        beak = (beak[0] + .1 % 1, beak[1], beak[2])

        scalar_colors = [hls_to_rgb(*color_pair) for color_pair in (eye, wing, body, beak)]
        colors = (tuple(int(color * 256) for color in color_pair) for color_pair in scalar_colors)

        colors = DuckyColors(*colors)

        return DuckyColors(*colors)


# If this file is executed we generate a random ducky and save it to disk
# A second argument can be given to seed the duck (that sounds a bit weird doesn't it)
if __name__ == "__main__":
    if len(sys.argv) > 1:
        random.seed(float(sys.argv[1]))

    ducky = make_ducky()
    print(*("{}: {}".format(key, value) for key, value in ducky._asdict().items()), sep="\n")
    ducky.image.save("ducky.png")
    print("Ducky saved to disk!")
