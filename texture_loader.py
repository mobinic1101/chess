from pathlib import Path
import inspect
import logging
import pygame
import settings


class TexturePack:
    def __init__(self, texture_dir: Path | str, name: str | None = None):
        texture_dir = (
            Path(texture_dir) if isinstance(texture_dir, str) else texture_dir
        ).absolute()

        # validating texture dir to be a directory
        if not texture_dir.is_dir():
            raise NotADirectoryError(
                f"{inspect.getfullargspec(TexturePack.__init__).args[1]} expected to be a directory, given: {texture_dir}"
            )

        self.texture_dir = texture_dir
        self.name = name if name is not None else texture_dir.name
        self.all_textures_paths = self._get_all_textures_paths()

        # check for messing textures
        logging.info("checking for messing textures...")
        messing_textures = self.find_messing_textures()
        if messing_textures:
            raise FileNotFoundError(
                f"messing texture for pack [{self.name}] [{', '.join(messing_textures)}]"
            )
        
        logging.info("loading all textures...")
        self.all_textures: dict[str, pygame.Surface] = self.load_all()

    def find_messing_textures(self):
        textures_names = [texture_name for texture_name in self.all_textures_paths]
        messing = []
        for texture_name in settings.TEXTURE_NAMES.values():
            if texture_name not in textures_names:
                messing.append(texture_name)
        return messing

    def _get_all_textures_paths(self) -> dict:
        all_textures = {}
        for texture in self.texture_dir.iterdir():
            if not texture.is_file():
                continue
            all_textures[texture.name] = texture
        return all_textures
    
    def get_texture_path(self, name: str) -> Path:
        """get texture path by its name (filename)
        Example .get_texture("board.png")

        Args:
            name (str): texture filename

        Returns:
            Path: path to texture
        """
        return self.all_textures_paths[name]

    def load_all(self) -> dict:
        all_textures = {}
        for texture_name, texture_path in self.all_textures_paths.items():
            all_textures[texture_name] = pygame.image.load(texture_path)
        return all_textures

    def get_texture(self, name: str, size: tuple[int, int] | None = None) -> pygame.Surface:
        """get texture by its name (filename)
        Example .get_texture("board.png", (500, 500))

        Args:
            name (str): texture filename
            size (tuple[width, height]): if given, the output texture will get scaled at the specified width and height

        Returns:
            pygame.Surface: texture/image (instance of pygame.Surface)
        """        
        texture = self.all_textures[name]
        if size is not None:
            texture = pygame.transform.scale(texture, size)
        return texture
    
    def __repr__(self):
        return f"TexturePack(name={self.name}, texture_dir={self.texture_dir})"   


class TexturePackLoader:
    def __init__(self, texture_dir: Path | str):
        texture_dir = (
            Path(texture_dir) if isinstance(texture_dir, str) else texture_dir
        ).absolute()
        logging.info("loading packs...")
        logging.info(f"looking for texture packs in {str(texture_dir)}")
        self.texture_dir = texture_dir
        self.all_packs: list[TexturePack] = self.load_packs()
        if not self.all_packs:
            raise FileNotFoundError("no texture packs found.")

    def load_packs(self) -> list[TexturePack]:
        all_packs = []
        for dir in self.texture_dir.iterdir():
            if not dir.is_dir():
                continue
            all_packs.append(TexturePack(dir))
        return all_packs

    def get_pack(self, name: str | None = None) -> TexturePack:
        """get texture pack. if pack not found, return default pack

        Args:
            name (str): pack name

        Returns:
            TexturePack: texture pack
        """
        default_pack: TexturePack
        for pack in self.all_packs:
            if pack.name == name:
                return pack
            elif pack.name == settings.DEFAULT_TEXTURE_PACK:
                default_pack = pack
        return default_pack
        
    def __repr__(self):
        return f"TexturePackLoader(texture_dir={self.texture_dir}, all_packs={self.all_packs})"


# testing
if __name__ == "__main__":
    import settings

    texture_loader = TexturePackLoader(settings.TEXTURE_DIR)
    print("texture dir: ", texture_loader.texture_dir)
    print("all_packs: ", texture_loader.all_packs)
    for pack in texture_loader.all_packs:
        print("pack: ", pack.name)
        print("pack_dir: ", pack.texture_dir)
        print("pack_textures_paths: ", pack.all_textures_paths)

    print("testing TexturePackLoader.get_pack() method")
    pack = texture_loader.get_pack()
    texture = pack.get_texture("b-pawn.png")
    print(texture)
