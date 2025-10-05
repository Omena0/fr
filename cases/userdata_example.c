// Example: Save and load user data to/from a file

void main() {
    println("Creating user data file...")
    
    // Write user data
    fd = fopen("/tmp/userdata.txt", "w")
    fwrite(fd, "Username: alice")
    fwrite(fd, " ")
    fwrite(fd, "Score: 1337")
    fwrite(fd, " ")
    fwrite(fd, "Level: 42")
    fclose(fd)
    
    println("Data saved!")
    
    // Read it back
    fd2 = fopen("/tmp/userdata.txt", "r")
    data = fread(fd2, -1)
    fclose(fd2)
    
    println("Loaded user data:")
    println(data)
    
    // Append achievement
    fd3 = fopen("/tmp/userdata.txt", "a")
    fwrite(fd3, " Achievement: First Login")
    fclose(fd3)
    
    // Read again
    fd4 = fopen("/tmp/userdata.txt", "r")
    updated = fread(fd4, -1)
    fclose(fd4)
    
    println("Updated user data:")
    println(updated)
}
