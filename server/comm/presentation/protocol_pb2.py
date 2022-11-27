# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: protocol.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0eprotocol.proto\x12\x0fprogramus.proto\x1a\x1bgoogle/protobuf/empty.proto\"\x1c\n\x0bTestMessage\x12\r\n\x05value\x18\x01 \x01(\t\"#\n\x0c\x45rrorMessage\x12\x13\n\x0b\x64\x65scription\x18\x01 \x01(\t\"!\n\x0cSetSessionId\x12\x11\n\tsessionId\x18\x01 \x01(\x04\"\x12\n\x10GetBoardsRequest\"v\n\x11GetBoardsResponse\x12\x37\n\x05\x62oard\x18\x01 \x03(\x0b\x32(.programus.proto.GetBoardsResponse.Board\x1a(\n\x05\x42oard\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x11\n\tfavourite\x18\x02 \x01(\x08\"\xe1\x01\n\x12\x44\x65viceUpdateStatus\x12:\n\x06status\x18\x01 \x01(\x0e\x32*.programus.proto.DeviceUpdateStatus.Status\x12\x1d\n\x10\x66lashingProgress\x18\x02 \x01(\x02H\x00\x88\x01\x01\x12\x12\n\x05image\x18\x03 \x01(\tH\x01\x88\x01\x01\"=\n\x06Status\x12\x0f\n\x0bUNREACHABLE\x10\x00\x12\t\n\x05READY\x10\x01\x12\x0c\n\x08\x46LASHING\x10\x02\x12\t\n\x05\x45RROR\x10\x03\x42\x13\n\x11_flashingProgressB\x08\n\x06_image\"\x91\x04\n\nFileUpload\x12\x10\n\x03uid\x18\x01 \x01(\x04H\x01\x88\x01\x01\x12\x32\n\x05start\x18\x64 \x01(\x0b\x32!.programus.proto.FileUpload.StartH\x00\x12\x30\n\x04part\x18\x65 \x01(\x0b\x32 .programus.proto.FileUpload.PartH\x00\x12\x34\n\x06\x66inish\x18g \x01(\x0b\x32\".programus.proto.FileUpload.FinishH\x00\x12\x34\n\x06result\x18h \x01(\x0e\x32\".programus.proto.FileUpload.ResultH\x00\x1ag\n\x05Start\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x0c\n\x04size\x18\x02 \x01(\x04\x12\x0e\n\x06\x63hunks\x18\x03 \x01(\r\x12\x32\n\x04type\x18\x04 \x01(\x0e\x32$.programus.proto.FileUpload.FileType\x1a%\n\x04Part\x12\x0e\n\x06partNo\x18\x01 \x01(\r\x12\r\n\x05\x63hunk\x18\n \x01(\x0c\x1a\x1a\n\x06\x46inish\x12\x10\n\x08\x63hecksum\x18\x01 \x01(\x0c\"\x18\n\x08\x46ileType\x12\x0c\n\x08\x46IRMWARE\x10\x00\"H\n\x06Result\x12\x06\n\x02OK\x10\x00\x12\x14\n\x10INVALID_CHECKSUM\x10\x01\x12\x0c\n\x08IO_ERROR\x10\x02\x12\x12\n\x0e\x41LREADY_EXISTS\x10\x03\x42\x07\n\x05\x65ventB\x06\n\x04_uid\"\xbf\x04\n\x0eGenericMessage\x12\x11\n\tsessionId\x18\x01 \x01(\x04\x12\x11\n\x07request\x18\x02 \x01(\x04H\x00\x12\x12\n\x08response\x18\x03 \x01(\x04H\x00\x12\x35\n\x0csetSessionId\x18\x64 \x01(\x0b\x32\x1d.programus.proto.SetSessionIdH\x01\x12+\n\theartbeat\x18\x65 \x01(\x0b\x32\x16.google.protobuf.EmptyH\x01\x12$\n\x02ok\x18\x66 \x01(\x0b\x32\x16.google.protobuf.EmptyH\x01\x12>\n\x10getBoardsRequest\x18\xc8\x01 \x01(\x0b\x32!.programus.proto.GetBoardsRequestH\x01\x12@\n\x11getBoardsResponse\x18\xc9\x01 \x01(\x0b\x32\".programus.proto.GetBoardsResponseH\x01\x12\x42\n\x12\x64\x65viceUpdateStatus\x18\xca\x01 \x01(\x0b\x32#.programus.proto.DeviceUpdateStatusH\x01\x12\x32\n\nfileUpload\x18\xcb\x01 \x01(\x0b\x32\x1b.programus.proto.FileUploadH\x01\x12-\n\x04test\x18\xad\x02 \x01(\x0b\x32\x1c.programus.proto.TestMessageH\x01\x12/\n\x05\x65rror\x18\xae\x02 \x01(\x0b\x32\x1d.programus.proto.ErrorMessageH\x01\x42\x04\n\x02idB\t\n\x07payloadb\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'protocol_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _TESTMESSAGE._serialized_start=64
  _TESTMESSAGE._serialized_end=92
  _ERRORMESSAGE._serialized_start=94
  _ERRORMESSAGE._serialized_end=129
  _SETSESSIONID._serialized_start=131
  _SETSESSIONID._serialized_end=164
  _GETBOARDSREQUEST._serialized_start=166
  _GETBOARDSREQUEST._serialized_end=184
  _GETBOARDSRESPONSE._serialized_start=186
  _GETBOARDSRESPONSE._serialized_end=304
  _GETBOARDSRESPONSE_BOARD._serialized_start=264
  _GETBOARDSRESPONSE_BOARD._serialized_end=304
  _DEVICEUPDATESTATUS._serialized_start=307
  _DEVICEUPDATESTATUS._serialized_end=532
  _DEVICEUPDATESTATUS_STATUS._serialized_start=440
  _DEVICEUPDATESTATUS_STATUS._serialized_end=501
  _FILEUPLOAD._serialized_start=535
  _FILEUPLOAD._serialized_end=1064
  _FILEUPLOAD_START._serialized_start=777
  _FILEUPLOAD_START._serialized_end=880
  _FILEUPLOAD_PART._serialized_start=882
  _FILEUPLOAD_PART._serialized_end=919
  _FILEUPLOAD_FINISH._serialized_start=921
  _FILEUPLOAD_FINISH._serialized_end=947
  _FILEUPLOAD_FILETYPE._serialized_start=949
  _FILEUPLOAD_FILETYPE._serialized_end=973
  _FILEUPLOAD_RESULT._serialized_start=975
  _FILEUPLOAD_RESULT._serialized_end=1047
  _GENERICMESSAGE._serialized_start=1067
  _GENERICMESSAGE._serialized_end=1642
# @@protoc_insertion_point(module_scope)
