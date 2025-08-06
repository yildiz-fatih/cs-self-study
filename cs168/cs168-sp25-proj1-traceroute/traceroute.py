import util

TRACEROUTE_MAX_TTL = 30

TRACEROUTE_PORT_NUMBER = 33434  # Cisco traceroute port number.

PROBE_ATTEMPT_COUNT = 3

def _bytes_to_bitstring(buffer: bytes) -> str:
    return ''.join(format(byte, '08b') for byte in buffer)

class IPv4:
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

def _parse_icmp(buf: bytes):
    outer_ipv4 = IPv4(buf[:20])
    if outer_ipv4.proto != 1 or len(buf) < outer_ipv4.header_len + 8:
        return None
    icmp = ICMP(buf[outer_ipv4.header_len:outer_ipv4.header_len + 8])
    
    inner_ipv4_offset = outer_ipv4.header_len + 8
    if len(buf) < inner_ipv4_offset + 20:
        return None
    inner_ipv4 = IPv4(buf[inner_ipv4_offset:inner_ipv4_offset + 20])
    
    udp_offset = inner_ipv4_offset + inner_ipv4.header_len
    if len(buf) < udp_offset + 8:
        return None
    udp = UDP(buf[udp_offset:udp_offset + 8])

    return outer_ipv4, icmp, inner_ipv4, udp

def traceroute(sendsock: util.Socket, recvsock: util.Socket, ip: str) \
        -> list[list[str]]:
    routers: list[list[str]] = []
    for ttl in range (1, TRACEROUTE_MAX_TTL + 1):
        sendsock.set_ttl(ttl)
        # --- send ---
        probed_ports: list[int] = []
        for i in range(PROBE_ATTEMPT_COUNT):
            port = TRACEROUTE_PORT_NUMBER + (ttl - 1) * PROBE_ATTEMPT_COUNT + i # unique port per probe&ttl
            sendsock.sendto("potato".encode(), (ip, port))
            probed_ports.append(port)

        # --- receive / collect ---
        seen_ports = set()
        responders = set()
        while len(seen_ports) < PROBE_ATTEMPT_COUNT:
            if not recvsock.recv_select():  # no packet ready now, don't block
                break
            
            buf, address = recvsock.recvfrom()
            if len(buf) < 20:
                continue

            # print(buf.hex()) # *** for debugging ***

            # --- parsing the incoming reply ---
            parsed = _parse_icmp(buf)
            if parsed is None:
                continue
            
            outer_ipv4, icmp, inner_ipv4, udp = parsed

            # skip if it's not a recognized packet or if it's a duplicate
            if udp.dst_port not in probed_ports or udp.dst_port in seen_ports:
                continue

            if icmp.type == 11 and icmp.code == 0: # Time Exceeded
                if inner_ipv4.dst != ip:
                    continue
                responders.add(outer_ipv4.src)
                seen_ports.add(udp.dst_port)
            elif icmp.type == 3 and icmp.code == 3: # Destination Unreachable
                destination_ip = inner_ipv4.dst
                if destination_ip != ip:
                    continue

                seen_ports.add(udp.dst_port)
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
