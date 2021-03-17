from package import Package, PackageWithTimer, Header, send_package
from socket import socket as Socket
from typing import List
from threading import Thread, Lock, Timer

import logging

logging.basicConfig(filename="./log/client.log", level=logging.INFO,
                    format="[%(asctime)s]: %(name)s %(levelname)s %(message)s")


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
        """
            The item of the list is class Package.
            len(waiting_for_send_buffer) = cwnd
        """
        self.waiting_for_send_buffer: List[Package] = []
        """
            Messages have been sent, but not received ACK from receiver.
            Every sent message has a timer, if timeout, the sent message should be retransmitted.
        Which means the message should be retrieved from sent_buffer to waiting_for_send_buffer.
        """
        self.sent_buffer: List[PackageWithTimer] = []
        self.socket: Socket = socket
        # todo: finish log
        logging.info(f"Client started")

        # self.start_receive_thread()
        self.start_send_thread()

    def start_send_thread(self):
        def temp():
            header = Header()
            header.set_message("good")
            self.socket.send(header.get_header_data())
            print("send good")

            send_timer = Timer(1, temp)
            send_timer.start()
            send_timer.join()

        temp()

    def start_receive_thread(self):
        while True:
            self.socket.recv(1024)

        # t = Thread()
        # t.start()
        # t.join()

    def transmit_the_buffer(self):
        """
            Transmit the messages in waiting_for_send_buffer to receiver.
            It's not transmit batch, but one by one.
        :return:
        """
        if len(self.waiting_for_send_buffer) == 0:
            logging.warning(f"[!] waiting_for_send_buffer is empty, can not be transmitted now!")
            return
        for i in range(len(self.waiting_for_send_buffer)):
            package = self.waiting_for_send_buffer[0]
            # todo: def a new method
            self.socket.send(package)
            # todo: complete log
            logging.debug(f"[.] Transmit message xxx")

            package_with_timer = PackageWithTimer(package)
            self.sent_buffer.append(package_with_timer)
            del self.waiting_for_send_buffer[0]
            package_with_timer.timer = Timer(self.rto, self.__check_ack, args=(package_with_timer,))
            logging.debug(f"[-] Message xxx has been appended to sent_buffer, timer started")

            # package_with_timer.timer=

            # item = list1[0]
            # del list1[0]
            # print(f"{item} {list1}")
        pass

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
        logging.debug(f"[.] Package xxx is out of time, will be retransmitted.")
