import struct
import pickle
from socket import socket as Socket
from enum import Enum


class Header:
    """
    ------------------------------------------------------------------------------------
    | 0                4B                  8B                  9B   13B          1024B |
    |         4B        |       4B         |        1B         | 4B  |      1011B      |
    | length of package | package hashcode | package data type | ACK | message string  |
    ------------------------------------------------------------------------------------

        The header has 1024 bytes data.
    length of package   :       Could be zero if there's no package, will be useful for message transfer only.
                            There's 4B for it, but it could not be greater than 1048576 (b'\x00\x10\x00\x00'),
                            for 1024*1024=1048576, namely the length of package could not be greater than 1MB.
    package hashcode    :       Should be a unique identifier, but could not be zero.
    ACK                 :       Acknowledge character, the value is one of the identifier of the packages. Zero
                            for none.
    package data type   :       See the supported types in PackageDataType below.
    message string      :       Must encode with utf-8, could store 1011 pure ASCII characters or 337 pure Chinese
                            characters.
    """

    class PackageDataType(Enum):
        BINARY = 0x00
        INT = 0x01
        UTF8_STR = 0x02

    def __init__(self, package_len: int = 0, package_hashcode: bytes = None, ack: bytes = b'\x00' * 4,
                 package_data_type: PackageDataType = PackageDataType.BINARY, message: str = None):
        """
        :param message:         If message is not none, then the value about package could be none.
        :param package_len:     1MBytes=1048576Bytes most
                                The max integer value of 4B is 4294967295, which
                            is far enough for the bytes'number of 1MB.
        """
        if (package_hashcode is not None and len(package_hashcode) != 4) or len(ack) != 4:
            raise BytesLengthError()
        if package_len != 0:
            if package_hashcode is None:
                raise LackOfPackageHashcodeException()
        if message is None and package_len == 0:
            raise LackOfMessageException()
        if message is not None and len(message.encode()) > 1011:
            raise MessageOutOfSizeException()

        self.package_len: bytes = package_len.to_bytes(length=4, byteorder='big', signed=False)
        self.package_hashcode: bytes = b'\x00' * 4 if package_hashcode is None else package_hashcode
        self.ack: bytes = ack
        self.package_data_type: bytes = package_data_type.value
        if message is None:
            self.message: bytes = b'\x00' * 1011
        else:
            temp: bytes = message.encode()
            if len(temp) < 1011:
                temp += b'\x00' * (1011 - len(temp))
            self.message: bytes = temp

        self.data: bytes = self.package_len + self.package_hashcode + self.ack + self.package_data_type + self.message
        assert len(self.data) == 1024


class Package:
    def __init__(self, payload: bytes, package_hashcode: bytes, message: str = None,
                 datatype: Header.PackageDataType = Header.PackageDataType.BINARY):
        """
            Every package has a header, the header contains the package's length,
        before sending the package, must send header first, otherwise the receiver
        has no idea to the package's size.
        """
        self.payload = payload
        self.header = Header(package_len=len(self.payload), package_hashcode=package_hashcode,
                             package_data_type=datatype, message=message)


class PackageWithTimer:
    def __init__(self, package):
        self.package = package
        self.timer = None
        """
            True means ack has been received on time.
            False means ack has not been received on time. 
        """
        self.ack_flag = False


def send_package(package: Package, sock: Socket):
    """
    :param package:
    :param sock:
    :return:
    """
    # parse header

    pass


def receive_package():
    pass


class LackOfMessageException(Exception):
    pass


class LackOfPackageHashcodeException(Exception):
    pass


class SendPackageException(Exception):
    pass


class BytesLengthError(ValueError):
    pass


class PackageOutOfSizeException(Exception):
    pass


class MessageOutOfSizeException(Exception):
    pass


class ReceivePackageException(Exception):
    pass
