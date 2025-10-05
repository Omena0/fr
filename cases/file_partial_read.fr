// !Chunk 1:\n0123456789\nChunk 2:\nABCDEFGHIJ

void main() {
    fd = fopen("/tmp/partial_test.txt", "w")
    fwrite(fd, "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    fclose(fd)
    
    fd2 = fopen("/tmp/partial_test.txt", "r")
    
    chunk1 = fread(fd2, 10)
    println("Chunk 1:")
    println(chunk1)
    
    chunk2 = fread(fd2, 10)
    println("Chunk 2:")
    println(chunk2)
    
    fclose(fd2)
}
