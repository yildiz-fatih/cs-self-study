import util

# Your program should send TTLs in the range [1, TRACEROUTE_MAX_TTL] inclusive.
# Technically IPv4 supports TTLs up to 255, but in practice this is excessive.
# Most traceroute implementations cap at approximately 30.  The unit tests
# assume you don't change this number.
TRACEROUTE_MAX_TTL = 30

# Cisco seems to have standardized on UDP ports [33434, 33464] for traceroute.
# While not a formal standard, it appears that some routers on the internet
# will only respond with time exceeeded ICMP messages to UDP packets send to
# those ports.  Ultimately, you can choose whatever port you like, but that
# range seems to give more interesting results.
TRACEROUTE_PORT_NUMBER = 33434  # Cisco traceroute port number.

# Sometimes packets on the internet get dropped.  PROBE_ATTEMPT_COUNT is the
# maximum number of times your traceroute function should attempt to probe a
# single router before giving up and moving on.
PROBE_ATTEMPT_COUNT = 3

def _bytes_to_bitstring(buffer: bytes) -> str:
    return ''.join(format(byte, '08b') for byte in buffer)

class IPv4:
    # Each member below is a field from the IPv4 packet header.  They are
    # listed below in the order they appear in the packet.  All fields should
    # be stored in host byte order.
    #
    # You should only modify the __init__() method of this class.
    version: int
    header_len: int  # Note length in bytes, not the value in the packet.
    tos: int         # Also called DSCP and ECN bits (i.e. on wikipedia).
    length: int      # Total length of the packet.
    id: int
    flags: int
    frag_offset: int
    ttl: int
    proto: int
    cksum: int
    src: str
    dst: str

    def __init__(self, buffer: bytes):
        bitstring = _bytes_to_bitstring(buffer)

        self.version = int(bitstring[0:4], 2)           # 4 bits
        self.header_len = int(bitstring[4:8], 2) * 4    # 4 bits
        self.tos = int(bitstring[8:16], 2)              # 8 bits
        self.length = int(bitstring[16:32], 2)          # 16 bits
        self.id = int(bitstring[32:48], 2)              # 16 bits
        self.flags = int(bitstring[48:51], 2)           # 3 bits
        self.frag_offset = int(bitstring[51:64], 2)     # 13 bits
        self.ttl = int(bitstring[64:72], 2)             # 8 bits
        self.proto = int(bitstring[72:80], 2)           # 8 bits
        self.cksum = int(bitstring[80:96], 2)           # 16 bits
        self.src = str(int(bitstring[96:104], 2)) + "." + str(int(bitstring[104:112], 2)) + "." + str(int(bitstring[112:120], 2)) + "." + str(int(bitstring[120:128], 2))   # 32 bits
        self.dst = str(int(bitstring[128:136], 2)) + "." + str(int(bitstring[136:144], 2)) + "." + str(int(bitstring[144:152], 2)) + "." + str(int(bitstring[152:160], 2))  # 32 bits

    def __str__(self) -> str:
        return f"IPv{self.version} (tos 0x{self.tos:x}, ttl {self.ttl}, " + \
            f"id {self.id}, flags 0x{self.flags:x}, " + \
            f"ofsset {self.frag_offset}, " + \
            f"proto {self.proto}, header_len {self.header_len}, " + \
            f"len {self.length}, cksum 0x{self.cksum:x}) " + \
            f"{self.src} > {self.dst}"


class ICMP:
    # Each member below is a field from the ICMP header.  They are listed below
    # in the order they appear in the packet.  All fields should be stored in
    # host byte order.
    #
    # You should only modify the __init__() function of this class.
    type: int
    code: int
    cksum: int

    def __init__(self, buffer: bytes):
        bitstring = _bytes_to_bitstring(buffer)

        self.type = int(bitstring[0:8], 2)     # 8 bits                   
        self.code = int(bitstring[8:16], 2)    # 8 bits
        self.cksum = int(bitstring[16:32], 2)  # 16 bits

    def __str__(self) -> str:
        return f"ICMP (type {self.type}, code {self.code}, " + \
            f"cksum 0x{self.cksum:x})"


class UDP:
    # Each member below is a field from the UDP header.  They are listed below
    # in the order they appear in the packet.  All fields should be stored in
    # host byte order.
    #
    # You should only modify the __init__() function of this class.
    src_port: int
    dst_port: int
    len: int
    cksum: int

    def __init__(self, buffer: bytes):
        bitstring = _bytes_to_bitstring(buffer)

        self.src_port = int(bitstring[0:16], 2)     # 16 bits                   
        self.dst_port = int(bitstring[16:32], 2)    # 16 bits
        self.len = int(bitstring[32:48], 2)         # 16 bits
        self.cksum = int(bitstring[48:64], 2)       # 16 bits

    def __str__(self) -> str:
        return f"UDP (src_port {self.src_port}, dst_port {self.dst_port}, " + \
            f"len {self.len}, cksum 0x{self.cksum:x})"


def traceroute(sendsock: util.Socket, recvsock: util.Socket, ip: str) \
        -> list[list[str]]:
    """ Run traceroute and returns the discovered path.

    Calls util.print_result() on the result of each TTL's probes to show
    progress.

    Arguments:
    sendsock -- This is a UDP socket you will use to send traceroute probes.
    recvsock -- This is the socket on which you will receive ICMP responses.
    ip -- This is the IP address of the end host you will be tracerouting.

    Returns:
    A list of lists representing the routers discovered for each ttl that was
    probed.  The ith list contains all of the routers found with TTL probe of
    i+1.   The routers discovered in the ith list can be in any order.  If no
    routers were found, the ith list can be empty.  If `ip` is discovered, it
    should be included as the final element in the list.
    """

    routers: list[list[str]] = []
    for ttl in range (1, TRACEROUTE_MAX_TTL + 1):
        sendsock.set_ttl(ttl)

        responders = set()
        for _ in range(PROBE_ATTEMPT_COUNT):
            sendsock.sendto("potato".encode(), (ip, TRACEROUTE_PORT_NUMBER))

            if recvsock.recv_select():
                buf, address = recvsock.recvfrom()

                # print(buf.hex()) # *** for debugging, REMOVE later ***

                outer_ipv4 = IPv4(buf[:20])
                icmp = ICMP(buf[outer_ipv4.header_len:outer_ipv4.header_len + 8])

                if icmp.type == 11 and icmp.code == 0: # Time Exceeded
                    responders.add(outer_ipv4.src)
                elif icmp.type == 3 and icmp.code == 3: # Destination Unreachable
                    # finish up and return
                    inner_ipv4_offset = outer_ipv4.header_len + 8
                    inner_ipv4 = IPv4(buf[inner_ipv4_offset:inner_ipv4_offset + 20])
                    destination_ip = inner_ipv4.dst

                    if destination_ip != ip:
                        continue

                    util.print_result([destination_ip], ttl)
                    routers.append([destination_ip])
                    return routers

        routers.append(list(responders))
        util.print_result(list(responders), ttl)
    return routers


if __name__ == '__main__':
    args = util.parse_args()
    ip_addr = util.gethostbyname(args.host)
    print(f"traceroute to {args.host} ({ip_addr})")
    traceroute(util.Socket.make_udp(), util.Socket.make_icmp(), ip_addr)
