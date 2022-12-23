import logging
from concurrent.futures import Future

from ..tasker import Tasker
from ..comm.protocol import OnFileUpload, FileUpload
from ..target.constants import FIRMWARE_PATH


# NOTE(bgrzesik): Maybe changing this to Actor would solve blocking
# other uploads
class UploadedFile(object):

    def __init__(self, name, rw=False):
        logging.debug(f"UploadedFile(): name={name} rw={rw}")
        self._name = f"{FIRMWARE_PATH}/{name}"
        self._file = open(self._name, "wb" if rw else "r")
        self._next_part = 0

    def append_part(self, part: FileUpload.Part) -> FileUpload.Result:
        logging.debug(f"append_part(): part_no={part.part_no} "
                      f"size={len(part.chunk)}")

        if self._next_part != part.part_no:
            return FileUpload.Result.IO_ERROR

        self._next_part += 1
        self._file.write(part.chunk)
        self._file.flush()

        return FileUpload.Result.OK

    def finish_upload(self, part: FileUpload.Finish) -> FileUpload.Result:
        logging.debug(f"finish_upload(): name={self._name}")

        self._file.close()
        self._file = open(self._name, "r")

        return FileUpload.Result.OK


class FileStore(Tasker):

    def __init__(self):
        Tasker.__init__(self)
        self._store = {}
        self._next_upload_id = 0
        self._uploads = {}

    @Tasker.assert_executor()
    def start_upload(self, name):
        logging.debug(f"start_upload(): name={name}")
        new_file = UploadedFile(name, rw=True)
        self._store[name] = new_file

        uid = self._next_upload_id
        self._next_upload_id += 1
        self._uploads[uid] = new_file

        return uid

    @Tasker.assert_executor()
    def get_upload(self, uid) -> UploadedFile:
        return self._uploads[uid]

    @Tasker.handler()
    def on_request(self, request: FileUpload.Request) -> FileUpload.Response:
        if isinstance(request, FileUpload.Start):
            start: FileUpload.Start = request
            uid = self.start_upload(start.name)

            return uid, FileUpload.Result.OK

        elif isinstance(request, FileUpload.Part):
            part: FileUpload.Part = request
            uploaded_file = self.get_upload(part.uid)

            if not uploaded_file:
                return -1, FileUpload.Result.IO_ERROR

            # TODO(bgrzesik): Defer to another TaskRunner
            return part.uid, uploaded_file.append_part(part)

        elif isinstance(request, FileUpload.Finish):
            finish: FileUpload.Finish = request
            uploaded_file = self.get_upload(finish.uid)

            if not uploaded_file:
                return -1, FileUpload.Result.IO_ERROR

            return finish.uid, uploaded_file.finish_upload(finish)

        else:
            assert False


class FileUploadHandler(OnFileUpload):

    def __init__(self, store: FileStore):
        self._store = store

    def on_request(self, request: FileUpload.Request) \
            -> Future[FileUpload.Response]:
        return self._store.on_request(request)
