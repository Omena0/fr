// !1\n2\n10\n20

struct Point {
    int x
    int y
}

struct Rectangle {
    Point topLeft
    Point bottomRight
}

void main() {
    Point p1 = Point(1, 2)
    Point p2 = Point(10, 20)
    Rectangle r = Rectangle(p1, p2)
    
    println(r.topLeft.x)
    println(r.topLeft.y)
    println(r.bottomRight.x)
    println(r.bottomRight.y)
}
