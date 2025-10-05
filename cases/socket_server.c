// Test socket server (needs manual client connection)

void main() {
    server = socket("inet", "stream")
    
    setsockopt(server, "SOL_SOCKET", "SO_REUSEADDR", 1)
    
    bind(server, "127.0.0.1", 8888)
    
    listen(server, 5)
    
    println("Server listening on port 8888...")
    
    client = accept(server)
    
    data = recv(client, 1024)
    println("Received: ")
    println(data)
    
    response = "HTTP/1.1 200 OK\r\nContent-Length: 13\r\n\r\nHello, World!"
    send(client, response)
    
    sclose(client)
    sclose(server)
    
    println("Server closed.")
}
