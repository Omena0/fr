// !Created 3 sockets

void main() {
    sock1 = socket("inet", "stream")
    sock2 = socket("inet", "dgram")
    sock3 = socket("inet", "stream")
    sclose(sock1)
    sclose(sock2)
    sclose(sock3)
    println("Created 3 sockets")
}
