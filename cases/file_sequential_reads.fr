// !Read: ABCDE\nRead: FGHIJ

void main() {
    fd = fopen("/tmp/test_sequential.txt", "w")
    fwrite(fd, "ABCDEFGHIJ")
    fclose(fd)
    
    fd2 = fopen("/tmp/test_sequential.txt", "r")
    first = fread(fd2, 5)
    second = fread(fd2, 5)
    fclose(fd2)
    
    println("Read: " + first)
    println("Read: " + second)
}
