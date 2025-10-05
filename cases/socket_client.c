// !Creating socket...\nSocket closed.

void main() {
    sock = socket("inet", "stream")
    println("Creating socket...")
    sclose(sock)
    println("Socket closed.")
}
