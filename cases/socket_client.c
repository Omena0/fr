// !Creating socket...
// !Socket closed.

void main() {
    sock = socket("inet", "stream")
    
    println("Creating socket...")
    
    sclose(sock)
    println("Socket closed.")
}
