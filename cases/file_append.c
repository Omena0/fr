// !File content:\nLine 1 Line 2 Line 3

void main() {
    fd = fopen("/tmp/append_test.txt", "w")
    fwrite(fd, "Line 1 ")
    fclose(fd)
    
    fd2 = fopen("/tmp/append_test.txt", "a")
    fwrite(fd2, "Line 2 ")
    fwrite(fd2, "Line 3")
    fclose(fd2)
    
    fd3 = fopen("/tmp/append_test.txt", "r")
    content = fread(fd3, -1)
    fclose(fd3)
    
    println("File content:")
    println(content)
}
