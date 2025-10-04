// !1\n2\n3\n4

struct Point {
    int x
    int y
}

void main() {
    Point p1 = Point(1, 2)
    Point p2 = Point(3, 4)
    
    list points = [p1, p2]
    
    println(points[0].x)
    println(points[0].y)
    println(points[1].x)
    println(points[1].y)
}
