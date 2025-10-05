// Comprehensive I/O test - demonstrates all file and socket operations

void main() {
    println("=== File I/O Tests ===")
    
    // Test 1: Write and read
    println("Test 1: Write and read")
    fd1 = fopen("/tmp/io_test.txt", "w")
    bytes = fwrite(fd1, "Test data 123")
    fclose(fd1)
    println("Wrote bytes:")
    println(str(bytes))
    
    fd2 = fopen("/tmp/io_test.txt", "r")
    content = fread(fd2, -1)
    fclose(fd2)
    println("Read content:")
    println(content)
    
    // Test 2: Append mode
    println("Test 2: Append mode")
    fd3 = fopen("/tmp/io_test.txt", "a")
    fwrite(fd3, " Appended!")
    fclose(fd3)
    
    fd4 = fopen("/tmp/io_test.txt", "r")
    updated = fread(fd4, -1)
    fclose(fd4)
    println("After append:")
    println(updated)
    
    // Test 3: Partial reads
    println("Test 3: Partial reads")
    fd5 = fopen("/tmp/io_test.txt", "r")
    part1 = fread(fd5, 5)
    part2 = fread(fd5, 5)
    fclose(fd5)
    println("Part 1:")
    println(part1)
    println("Part 2:")
    println(part2)
    
    println("")
    println("=== Socket Tests ===")
    
    // Test 4: Socket creation
    println("Test 4: Socket creation")
    sock = socket("inet", "stream")
    println("TCP socket created with ID:")
    println(str(sock))
    
    // Test 5: Socket options
    println("Test 5: Socket options")
    setsockopt(sock, "SOL_SOCKET", "SO_REUSEADDR", 1)
    println("Set SO_REUSEADDR option")
    
    // Test 6: Close socket
    println("Test 6: Close socket")
    sclose(sock)
    println("Socket closed")
    
    // Test 7: UDP socket
    println("Test 7: UDP socket")
    udp = socket("inet", "dgram")
    println("UDP socket created with ID:")
    println(str(udp))
    sclose(udp)
    println("UDP socket closed")
    
    println("")
    println("=== All I/O tests completed successfully! ===")
}
