from package import Package, PackageWithTimer, Header, send_package, receive_package, PackageDataType
from socket import socket as Socket
from typing import List
from threading import Thread, Lock, Timer
from app.utils import Logger, int2bytes
import time

log = Logger()


class Client:
    def __init__(self, socket, initial_cwnd: int = 1, initial_ssthresh: int = 24, initial_rto: int = 500):
        """
        :param socket:
        :param initial_cwnd: Congestion window, default 1 package
        :param initial_ssthresh: Slow start threshold, default 24 packages
        :param initial_rto: Retransmission Time-Out, default 500ms
        """
        self.cwnd: int = initial_cwnd
        self.ssthresh: int = initial_ssthresh
        self.rto: int = initial_rto

        self.__data_buffer_lock = Lock()
        """
            The list of produce result, the result will be placed into the list as soon as the data be produced.
        """
        self.__data_buffer: List[Package] = []

        """
            The item of the list is class Package, max len(waiting_for_send_buffer) = cwnd
            The header in the buffer may be none, should be checked or generated before transmitting.
        """
        self.waiting_for_send_buffer: List[Package] = []
        """
            Messages have been sent, but not received ACK from receiver.
            Every sent message has a timer, if timeout, the sent message should be retransmitted.
        Which means the message should be retrieved from sent_buffer to waiting_for_send_buffer.
        """
        self.sent_buffer: List[PackageWithTimer] = []
        self.socket: Socket = socket

        # self.start_receive_thread()
        self.start_send_thread()

    def add_data(self, item: Package):
        self.__data_buffer.append(item)

    def start_send_thread(self):
        def temp():
            temp_data: int = 0
            while True:
                package = Package(payload=int2bytes(temp_data), data_type=PackageDataType.INT)
                package.generate_default_header()
                package.get_header().set_package_seq(temp_data)

                send_package(package, self.socket)
                temp_data += 1
                time.sleep(1)

        t = Thread(target=temp)
        t.start()
        t.join()

    # def start_send_thread(self):
    #     """
    #         When the cwnd is full, then send the buffer
    #     :return:
    #     """
    #     count = 1
    #
    #     def temp(**kwargs):
    #         nonlocal count
    #         # count = kwargs['count']
    #
    #         header = Header()
    #         header.set_message("good")
    #         header.set_package_hashcode(
    #             count.to_bytes(length=header.HEADER_PACKAGE_HASHCODE_LEN, byteorder='big', signed=False))
    #         count += 1
    #
    #         self.socket.send(header.get_header_data())
    #         print("send good")
    #
    #         send_timer = Timer(1, temp)
    #         send_timer.start()
    #         send_timer.join()
    #
    #     temp()

    def start_receive_thread(self):
        def temp():
            while True:
                result = receive_package(self.socket)
                if isinstance(result, Header):
                    header = result
                    log.debug(f"<- message: \"{header.get_message()}\" "
                              f"| hash: {header.get_package_hashcode()}")
                else:
                    package = result
                    header = result.get_header()
                    self.start_consume_thread(package)
                    log.debug("<- " + package.get_desc())

        t = Thread(target=temp)
        t.start()

    def start_consume_thread(self, package: Package):
        """
            Do calculate
        :param package:
        :return:
        """

        def temp():
            payload: List[int] = package.get_payload(parse=True)
            header = package.get_header()
            package_hashcode = header.get_package_hashcode(parse=True)

            log.info(f"--> Consuming package {package_hashcode}, job started.")
            # todo: different type of calculation methods
            cal_result: int = 0
            for item in payload:
                cal_result += item
            time.sleep(2)
            log.info(f"<-- Finished  package {package_hashcode}, job ended.")
            # Sending the result to proxy
            result_package = Package(payload=int2bytes(cal_result), data_type=PackageDataType.INT)
            result_package.generate_default_header(msg=f"calculate result of {package_hashcode}")
            result_package.get_header().set_ack(header.get_package_hashcode())
            send_package(result_package, self.socket)
            log.info(f"-> {result_package.get_desc()}")

        t = Thread(target=temp)
        t.start()
        # No join() allowed here

    def transmit_the_buffer(self):
        """
            Transmit the package in waiting_for_send_buffer to receiver. Only when the buffer is full
        or the job is finished, then the packages should be sent.
            It's not transmit batch, but one by one.
        :return:
        """
        if len(self.waiting_for_send_buffer) == 0:
            log.warning(f"[!!] waiting_for_send_buffer is empty, can not be transmitted now!")
            return
        for i in range(len(self.waiting_for_send_buffer)):
            package = self.waiting_for_send_buffer[0]
            if package.get_header() is None:
                package.generate_default_header()

            send_package(package, self.socket)

            header = package.get_header()
            log.debug(f"[->] Transmit package {header.get_package_hashcode().hex()}\t "
                      f"message: {header.get_message(parse=True)}\t "
                      f"payload size: {header.get_package_len(parse=True)}"
                      )

            package_with_timer = PackageWithTimer(package)
            self.sent_buffer.append(package_with_timer)
            del self.waiting_for_send_buffer[0]

            # todo: check ack

            # package_with_timer.timer = Timer(self.rto, self.__check_ack, args=(package_with_timer,))

            # logging.debug(f"[--] Message xxx has been appended to sent_buffer, timer started")

            # package_with_timer.timer=

            # item = list1[0]
            # del list1[0]
            # print(f"{item} {list1}")

    def __check_ack(self, package_with_timer: PackageWithTimer):
        """
            It's for timer function, can not be called directly.
            If this client received the specific package ACK from proxy on time,
        then this package will be removed from sent_buffer, which means the package
        has been sent successfully. Otherwise, the package had been aborted by the
        receiver, has to be resent.
        :param package_with_timer
                    The ack_flag of package_with_timer should always not be true,
                because if once package has been sent successfully (received the
                ACK of the package), the package object with the timer should be
                destroyed immediately.
        :return:
        """
        # todo: double check
        if package_with_timer.ack_flag:
            return
        # out of time
        package = package_with_timer.package
        self.waiting_for_send_buffer.append(package)
        self.sent_buffer.remove(package_with_timer)
        log.debug(f"[.] Package xxx is out of time, will be retransmitted.")
