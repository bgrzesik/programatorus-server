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


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0eprotocol.proto\x12\x0fprogramus.proto\x1a\x1bgoogle/protobuf/empty.proto\"\x1c\n\x0bTestMessage\x12\r\n\x05value\x18\x01 \x01(\t\"#\n\x0c\x45rrorMessage\x12\x13\n\x0b\x64\x65scription\x18\x01 \x01(\t\"!\n\x0cSetSessionId\x12\x11\n\tsessionId\x18\x01 \x01(\x04\"\xc0\x02\n\x0eGenericMessage\x12\x11\n\tsessionId\x18\x01 \x01(\x04\x12\x11\n\trequestId\x18\x02 \x01(\x04\x12\x12\n\nresponseId\x18\x03 \x01(\x04\x12\x35\n\x0csetSessionId\x18\x64 \x01(\x0b\x32\x1d.programus.proto.SetSessionIdH\x00\x12+\n\theartbeat\x18\x65 \x01(\x0b\x32\x16.google.protobuf.EmptyH\x00\x12-\n\x04test\x18\xc9\x01 \x01(\x0b\x32\x1c.programus.proto.TestMessageH\x00\x12/\n\x05\x65rror\x18\xca\x01 \x01(\x0b\x32\x1d.programus.proto.ErrorMessageH\x00\x12%\n\x02ok\x18\xcb\x01 \x01(\x0b\x32\x16.google.protobuf.EmptyH\x00\x42\t\n\x07payloadb\x06proto3')

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
  _GENERICMESSAGE._serialized_start=167
  _GENERICMESSAGE._serialized_end=487
# @@protoc_insertion_point(module_scope)
