terraform {
 
  backend "http" {
    address        = "http://localhost:8080/state_identifier"
    lock_address   = "http://localhost:8080/state_identifier/lock"
    unlock_address = "http://localhost:8080/state_identifier/unlock"
    # Optional: (Authentication token if implemented or any other required headers)
  }
}
