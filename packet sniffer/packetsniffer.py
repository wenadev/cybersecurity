import socket
import struct
import sys
import re
 
# receive a datagram
def getData(socket):
    raw_data = ''
    try:
        raw_data, address = socket.recvfrom(65565)
    except:
        print ("An error happened: ")
        sys.exc_info()
    
    return raw_data
 
#unpack version number and internet header length
def versionIHL(u_data):
    version = u_data >> 4
    IHL = (u_data & 0x0F) *4
    
    return version, IHL


#get the type of services
def diff_services(u_data):
    precedence = {0: "Routine", 1: "Priority", 2: "Immediate", 3: "Flash", 
                  4: "Flash override", 5: "CRITIC/ECP", 6: "Internetwork control", 
                  7: "Network control"}
    delay = {0: "Normal delay", 1: "Low delay"}
    throughput = {0: "Normal throughput", 1: "High throughput"}
    reliability = {0: "Normal reliability", 1: "High reliability"}
    monetary = {0: "Normal monetary cost", 1: "Minimize monetary cost"}
    
    P = u_data >> 5
    
    D = u_data & 0x10
    D = D >> 4
    
    T = u_data & 0x8
    T = T >> 3
    
    R = u_data & 0x4
    R = R >> 2
    
    M = u_data & 0x02
    M = M >> 1
    
    return precedence[P] + '\n\t\t\t' + delay[D] + '\n\t\t\t' + throughput[T] + '\n\t\t\t' + reliability[R] + '\n\t\t\t' + monetary[M]
    
    
def flags_fragment(u_data):
    flagR = {0: 'Reserved'}
    flagDF = {0: 'Fragment if necessary', 1: 'Do not fragment'}
    flagMF = {0: 'This is the last fragment', 1: 'More fragments follow this fragment'}
    
    R = u_data & 0x8000
    R = R >> 15
    
    DF = u_data & 0x4000
    DF = DF >> 14
    
    MF = u_data & 0x2000
    MF = MF >> 13
    
    fragment = u_data & 0x1FFF
    
    return flagR[R] + "\n\t\t\t" + flagDF[DF] + '\n\t\t\t' + flagMF[MF], fragment

def protocol(u_data):
    file = open('protocol.txt', 'r')
    p = file.read()
    protocol = re.findall(r'\9n', str(u_data) +'(?:.)+\n', p)

    if protocol:
        protocol == protocol[0]
        protocol = protocol.replace('\n','')
        protocol = protocol.replace(str(u_data), '')
        protocol = protocol.lstrip()
        
        return protocol
    
    else:
        return "Did not find any protocol"


# the public network interface
HOST = socket.gethostbyname(socket.gethostname())


#unpacking data    
def main(d):
    #! means sets it as a network data as network bytes and data on our computer are different
    #H is small unsigned int- 2 bytes
    #B is a single byte
    #s signfies string
    #get first 20 bytes in the IP packet 
    unpacked = struct.unpack('!BBHHHBBH4s4s', data[:20])
    
    version, header_length = versionIHL(unpacked[0]) 
    services = diff_services(unpacked[1])
    total_length = unpacked[2]
    identification = unpacked[3]
    flags, fragment_offset = flags_fragment(unpacked[4])
    ttl = unpacked[5]
    proto = protocol(unpacked[6])
    checksum= unpacked[7]
    source_IP = socket.inet_ntoa(unpacked[8])
    dest_IP = socket.inet_ntoa(unpacked[9])
     
    return version, header_length, services, total_length, identification, flags, fragment_offset, ttl, protocol, checksum, source_IP, dest_IP

# create a raw socket and bind it to the public interface
s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_IP)

s.bind((HOST, 0))

# Include IP headers
s.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

# receive all packages
s.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)

#get IP header data
data = getData((s))

print("Captured packet")
print("----------------")
print ("Version:\t\t",  str(main(data)[0]))
print ("Header Length:\t\t", str(main(data)[1]), " bytes")
print ("Type of Service:\t", str(main(data)[2]))
print("Size/Total Length:\t", str(main(data)[3]))
print ("ID:\t\t\t", str(main(data)[4]))
print ("Flags:\t\t\t", str(main(data)[5]))
print ("Fragment offset:\t", str(+main(data)[6]))
print ("TTL:\t\t\t", str(+main(data)[7]))
print ("Protocol:\t\t", str(+main(data)[8]))
print ("Checksum:\t\t", str(main(data)[9]))
print ("Source:\t\t\t", str(main(data)[10]))
print ("Destination:\t\t", str(main(data)[11]))
print ("Payload:\n", data[20:])
