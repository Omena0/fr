// !5

void main() {
    fd = fopen("/tmp/test_fwrite_return.txt", "w")
    bytes = fwrite(fd, "Hello")
    fclose(fd)
    println(str(bytes))
}
