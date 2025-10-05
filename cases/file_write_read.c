// !File content:\nHello, World! This is a test file.

void main() {
    fd = fopen("/tmp/test_lang2.txt", "w")
    fwrite(fd, "Hello, World! This is a test file.")
    fclose(fd)
    
    fd2 = fopen("/tmp/test_lang2.txt", "r")
    content = fread(fd2, -1)
    fclose(fd2)
    
    println("File content:")
    println(content)
}
