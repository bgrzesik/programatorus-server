# import glob
# import pickledb
#
#
# class ConfigFilesRepository(object):
#
#
#
#     def __init__(self, files_path: str, db_file_path: str):
#         super().__init__()
#         self.path = files_path
#
#         self.all = glob.glob(f"{files_path}/*.cfg")
#         self.all = sorted(list(map(lambda x: x.split("/")[-1], self.all)))
#
#         self.store = pickledb.load(db_file_path, auto_dump=True)
#         if not self.store.exists('favorites'):
#             self.store.set('favorites', [])
#         self.store.append('favorites', ["DUPA"])
#         print(self.store.get('favorites'))
#
# if __name__ == "__main__":
#     cfp = ConfigFilesRepository("/home/pi/openocd/tcl/target", "./store.db")