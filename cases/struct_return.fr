// !0\n0\n5\n10

struct Point {
    int x
    int y
}

Point createPoint(int x, int y) {
    return Point(x, y)
}

void main() {
    Point p1 = createPoint(0, 0)
    Point p2 = createPoint(5, 10)
    
    println(p1.x)
    println(p1.y)
    println(p2.x)
    println(p2.y)
}
