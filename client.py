from package import Package, PackageWithTimer, Header, send_package, receive_package, PackageDataType
from socket import socket as Socket
from typing import List
from threading import Thread, Lock, Timer
from app.utils import Logger, int2bytes, int_list_to_bytes
import time
from queue import Queue, LifoQueue

log = Logger()


class SeqData:
    def __init__(self, seq: int, data):
        self.seq = seq
        self.data = data

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"({self.seq},{self.data})"


class Client:
    BUFFER_MAX = 50

    def __init__(self, socket, initial_cwnd: int = 1, initial_ssthresh: int = 24, sending_time_interval=0.5):
        """
        :param socket:
        :param initial_cwnd:                Congestion window, default 1 package.
        :param initial_ssthresh:            Slow start threshold, default 24 packages.
        :param sending_time_interval:       The buffer data will be boxed then send every sending_time_interval
                                        second, default 0.5s.
        """
        self.cwnd: int = initial_cwnd
        self.ssthresh: int = initial_ssthresh
        self.sending_time_interval = sending_time_interval

        # The item of the queue is class SeqData, it's thead-safe, and the data in queue is ordered.
        self.data_buffer: Queue = Queue(maxsize=Client.BUFFER_MAX)

        """
            Every client has only one discarded package, this filed will be reset to None after resending
        successfully.
        """
        self.discard_package: Package = None
        # The content of resent_buffer is from resent_package unpacking
        self.resent_buffer: LifoQueue = LifoQueue(maxsize=Client.BUFFER_MAX)
        self.resending_flag: bool = False
        self.total_resent: int = -1
        self.current_resent: int = -1

        self.socket: Socket = socket

        self.produce()
        self.start_send_thread()

    def produce(self):
        def temp():
            temp_data: int = 0
            while True:
                # simulating producing data
                time.sleep(0.2)
                temp_data += 1

                buffer: Queue = self.data_buffer
                if not buffer.full():
                    buffer.put(SeqData(seq=temp_data - 1, data=temp_data))

        t = Thread(target=temp)
        t.start()

    def pack_data_buffer(self, buffer: Queue, pack_length) -> Package:
        # buffer_length = buffer.qsize()
        payload: List[int] = []
        seq: int = -1
        pack_length = min(pack_length, buffer.qsize())
        for i in range(pack_length):
            seq_data: SeqData = buffer.get()
            payload.append(seq_data.data)
            if i == 0:
                seq = seq_data.seq

        package = Package(payload=int_list_to_bytes(payload), data_type=PackageDataType.INT)
        package.generate_default_header()
        package.get_header().set_package_seq(seq)
        return package

    def unpack_data_buffer(self, package: Package):
        payload: List[int] = package.get_payload(parse=True)
        header = package.get_header()
        seq: int = header.get_package_seq(parse=True)
        # put the data into stack inverted order
        for i in range(len(payload) - 1, -1, -1):
            seq_data = SeqData(seq=seq + i, data=payload[i])
            self.resent_buffer.put(seq_data)
        log.debug(f"resent buffer: {self.resent_buffer.queue}")

    def start_send_thread(self):
        def temp():
            buffer = self.data_buffer
            resent_buffer = self.resent_buffer
            if buffer.empty() and resent_buffer.empty():
                _t = Timer(self.sending_time_interval, temp)
                _t.start()
                return
            if not resent_buffer.empty():
                package = self.pack_data_buffer(resent_buffer, self.cwnd)
                total_package_length = len(self.discard_package.get_payload(parse=True))
                log.info(f"resent package {self.discard_package.get_header().get_package_hashcode(parse=True)} "
                         f"| {total_package_length - resent_buffer.qsize()} of {total_package_length} "
                         f"| current package {package.get_header().get_package_hashcode(parse=True)}, cwnd: {self.cwnd}"
                         )
                self.resending_flag = True
            else:
                package = self.pack_data_buffer(buffer, self.cwnd)
            try:
                send_package(package, self.socket)
            except (ConnectionAbortedError, ConnectionResetError):
                log.info("Connection has been closed by proxy, remote job finished.")
                return
            log.debug(
                f"<- {package.get_desc()}"
            )

            # There should be a header contains ack received after every package sending
            header = receive_package(self.socket)
            message = header.get_message(parse=True)
            ack = header.get_ack(parse=True)
            log.debug(
                f"-> ack: {ack} "
                f"| message: \"{message}\" "
            )
            # ---> sending failed
            if message == Header.MSG_PACKAGE_DISCARD:
                if self.resending_flag:
                    log.warning(f"The resent package also be discarded!")
                else:
                    log.warning(f"package {ack} has been discarded, will be resend.")
                    self.discard_package = package
                self.unpack_data_buffer(package)
                self.cwnd = 1
                self.ssthresh /= 2
            # <--- sending failed
            # ---> sending successfully
            else:
                # resending finished
                if self.resending_flag and self.resent_buffer.empty():
                    self.resending_flag = False
                    self.discard_package = None
                if self.cwnd >= self.ssthresh:
                    self.cwnd += 1
                    self.ssthresh += 1
                # slow start
                else:
                    self.cwnd *= 2
            # <--- sending successfully
            _t = Timer(self.sending_time_interval, temp)
            _t.start()

        # check the buffer every second, if the buffer is not empty, combine the buffer into one
        t = Timer(self.sending_time_interval, temp)
        t.start()

    # ---------------------------> deprecated for now <---------------------------------------
    def start_receive_thread(self):
        def temp():
            while True:
                try:
                    result = receive_package(self.socket)
                except ConnectionAbortedError:
                    log.info("Connection has been closed by proxy, remote job finished.")
                    return
                if isinstance(result, Header):
                    header = result
                    message = header.get_message(parse=True)
                    ack = header.get_ack(parse=True)
                    log.debug(f"-> message: \"{message}\" "
                              f"| ack: {ack} "
                              f"| hash: {header.get_package_hashcode(parse=True)}")
                    # resend the package
                    if message == Header.MSG_PACKAGE_DISCARD:
                        log.warning(f"package {ack} has been discarded, will be resend.")
                else:
                    package = result
                    header = result.get_header()
                    self.start_consume_thread(package)
                    log.debug("-> " + package.get_desc())

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
    # ---------------------------> deprecated for now <---------------------------------------
