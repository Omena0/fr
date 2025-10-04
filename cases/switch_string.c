// !weekday

void main() {
    str day = "monday"
    
    switch (day) {
        case "monday":
            println("weekday")
        case "tuesday":
            println("weekday")
        case "wednesday":
            println("weekday")
        case "thursday":
            println("weekday")
        case "friday":
            println("weekday")
        case "saturday":
            println("weekend")
        case "sunday":
            println("weekend")
        default:
            println("invalid day")
    }
}
