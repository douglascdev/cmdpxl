import sys
from pathlib import Path
from typing import Tuple, Union

import click
import pygame as pg
import pygame.font

black, white, red = pg.Color(20, 20, 20), pg.Color(255, 255, 255), pg.Color(150, 0, 0)


def resize_surface_by_percentage(surface: pg.Surface, percentage_of_screen: int) -> pg.Surface:
    screen = pygame.display.get_surface()
    new_image_resolution = [xy * percentage_of_screen // 100 for xy in (screen.get_width(), screen.get_height())]
    return pg.transform.scale(surface, new_image_resolution)


def new_text_surface(text: str, size: int = 12, color: pg.color.Color = black):
    default_font = (Path(__file__).parent / ".." / "assets" / "fonts" / "PressStart2P-Regular.ttf").resolve()
    font = pygame.font.Font(default_font, size)
    return font.render(text, False, color, None)


def blit_text(draw: Union[str, pg.Surface], coord: Tuple[int, int]):
    surface = draw if isinstance(draw, pg.Surface) else new_text_surface(str(draw))
    pg.display.get_surface().blit(surface, coord)


def rect_screen_center(rect: pg.Rect, center_x=False, center_y=False) -> Tuple[int, int]:
    screen = pygame.display.get_surface()
    rect = rect.copy()

    if center_x:
        rect.x = screen.get_rect().centerx - rect.w // 2

    if center_y:
        rect.y = screen.get_rect().centery - rect.h // 2

    return rect.x, rect.y


def draw_welcome_msg(func):
    def wrapper():
        click.clear()
        click.echo(click.style("CMDPXL - A TOTALLY PRACTICAL IMAGE EDITOR", fg='red'))
        func()

    return wrapper


@draw_welcome_msg
@click.command(name="cmdpxl")
@click.option(
    "--filepath",
    "-f",
    prompt="File path",
    help="Path for the file you want to open",
    type=click.Path(),
)
@click.option(
    "--resolution",
    "-res",
    help="Image height and width separated by a comma, e.g. 20,10 for a 20x10 image. Note that no spaces can be used.",
)
def main(filepath, resolution):
    img_size = list(
        map(int, resolution.split(","))
        if resolution
        else map(int, (input(f"Image {x}: ") for x in ("width", "height")))
    )

    pg.init()
    screen = pg.display.set_mode((600, 600), pg.RESIZABLE)
    app_name = click.get_current_context().command.name
    pg.display.set_caption(app_name)

    path = Path(filepath)
    image = pg.image.load(path) if path.exists() and path.is_file() else pg.Surface(img_size)

    cursor_rect = None

    line_width = 6
    cursor_line_width = line_width // 4

    clock = pg.time.Clock()

    while True:
        screen.fill(black)

        # Draws header text
        header_text = f"{app_name}: {path.name} ({image.get_width()}x{image.get_height()})"
        text_surface = new_text_surface(header_text, color=red)
        text_rect = rect_screen_center(text_surface.get_rect().move(0, 10), center_x=True)
        blit_text(text_surface, text_rect)

        # Draws the selected image
        resized_img = resize_surface_by_percentage(image, 30)
        img_screen_pos = rect_screen_center(resized_img.get_rect(), center_x=True, center_y=True)
        screen.blit(resized_img, img_screen_pos)

        # Draws the rectangle around the image
        x, y = img_screen_pos[0] - line_width, img_screen_pos[1] - line_width
        w, h = resized_img.get_rect().w + line_width, resized_img.get_rect().h + line_width
        rectangle_rect = pg.Rect((x, y), (w, h))
        pg.draw.rect(screen, white, rectangle_rect, width=line_width)

        # Initializes cursor_rect value
        if not cursor_rect:
            x, y = img_screen_pos[0] - cursor_line_width - 2, img_screen_pos[1] - cursor_line_width - 2
            w, h = resized_img.get_width() // image.get_width(), resized_img.get_height() // image.get_height()
            cursor_rect = pg.Rect((x, y), (w, h))

        # Draws the rectangle that corresponds to the cursor
        pg.draw.rect(screen, white, cursor_rect, width=cursor_line_width)

        # Handles user events
        for event in pg.event.get():
            if event.type == pg.QUIT:
                sys.exit()

            elif event.type == pg.KEYDOWN:
                x_mov = resized_img.get_width() // (image.get_width())
                y_mov = resized_img.get_height() // (image.get_height())

                if event.key == pg.K_UP:
                    cursor_rect.move_ip(0, -x_mov)
                elif event.key == pg.K_DOWN:
                    cursor_rect.move_ip(0, x_mov)
                elif event.key == pg.K_RIGHT:
                    cursor_rect.move_ip(y_mov, 0)
                elif event.key == pg.K_LEFT:
                    cursor_rect.move_ip(-y_mov, 0)

                print(f"(x={cursor_rect.x}, y={cursor_rect.y})")

        pg.display.flip()

        clock.tick(60)


if __name__ == "__main__":
    main()
