// !42\n3.14\nhello\ntrue

struct Mixed {
    int num
    float pi
    str text
    bool flag
}

void main() {
    Mixed m = Mixed(42, 3.14, "hello", true)
    
    println(m.num)
    println(m.pi)
    println(m.text)
    println(m.flag)
}
