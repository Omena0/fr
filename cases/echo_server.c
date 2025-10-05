// Simple echo server example
// Listens on port 9999 and echoes back any data received

void main() {
    println("Starting echo server on port 9999...")
    
    server = socket("inet", "stream")
    setsockopt(server, "SOL_SOCKET", "SO_REUSEADDR", 1)
    bind(server, "127.0.0.1", 9999)
    listen(server, 5)
    
    println("Server ready! Waiting for connection...")
    println("Connect with: telnet 127.0.0.1 9999")
    
    client = accept(server)
    println("Client connected!")
    
    send(client, "Welcome to echo server! Type something:")
    
    data = recv(client, 1024)
    println("Received from client:")
    println(data)
    
    send(client, "Echo: ")
    send(client, data)
    
    sclose(client)
    sclose(server)
    
    println("Server closed.")
}
