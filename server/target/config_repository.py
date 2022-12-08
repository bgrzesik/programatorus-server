import glob
from . import const
import pickledb

from server.comm.protocol import BoardsData, Board, FirmwareData, Firmware

FAV_BOARDS = 'fav_boards'
FAV_FIRMWARE = 'fav_firmware'


def extract_filename(path: str):
    return path.split("/")[-1]

class ConfigFilesRepository():

    def __init__(self):
        super().__init__()
        self.all_boards = glob.glob(f"{const.BOARDS_PATH}/*.cfg")
        self.all_boards = sorted(list(map(extract_filename, self.all_boards)))

        self.all_firmware = glob.glob(f"{const.FIRMWARE_PATH}/*")
        self.all_firmware = sorted(list(map(extract_filename, self.all_firmware)))

        self._store = pickledb.load(const.DB_PATH, auto_dump=False)

        if not self._store.exists(FAV_BOARDS):
            self._store.set(FAV_BOARDS, [])

        if not self._store.exists(FAV_FIRMWARE):
            self._store.set(FAV_FIRMWARE, [])

    def set_fav_boards(self, favorites: list[str]):
        self._store.set(FAV_BOARDS, favorites)
        self._store.dump()

    def get_fav_boards(self) -> list[str]:
        return self._store.get(FAV_BOARDS)

    def get_all_boards(self) -> list[str]:
        return self.all_boards

    def get_all_firmware(self) -> list[str]:
        return self.all_firmware

    def set_fav_firmwares(self, favorites: list[str]):
        self._store.set(FAV_FIRMWARE, favorites)
        self._store.dump()
        self._store.get(FAV_FIRMWARE)

    def get_fav_firmwares(self) -> list[str]:
        return self._store.get(FAV_FIRMWARE)


class BoardsService(object):

    def __init__(self, repository: ConfigFilesRepository):
        super().__init__()
        self.repository = repository

    def get(self) -> BoardsData:
        fav = self.repository.get_fav_boards()
        fav_set = set(fav)

        return BoardsData(
            all=list(map(lambda s: Board(s, s in fav_set),  self.repository.get_all_boards())),
            favorites=list(map(lambda s: Board(s, True),  fav)),
        )

    def put(self, data: BoardsData):
        print(data)
        self.repository.set_fav_boards(list(map(lambda x: x.name, data.favorites)))


class FirmwareService(object):

    def __init__(self, repository: ConfigFilesRepository):
        super().__init__()
        self.repository = repository

    def get(self) -> FirmwareData:
        fav = self.repository.get_fav_firmwares()
        fav_set = set(fav)

        val = FirmwareData(
            all=list(map(lambda s: Firmware(s, s in fav_set), self.repository.get_all_firmware())),
            favorites=list(map(lambda s: Firmware(s, True), fav)),
        )
        print(val)
        return val

    def put(self, data: FirmwareData):
        print("put", data)
        self.repository.set_fav_firmwares(list(map(lambda x: x.name, data.favorites)))
