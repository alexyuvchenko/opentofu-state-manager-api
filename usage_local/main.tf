terraform {
 
  backend "http" {
    address        = "http://localhost:8000/state_identifier"
    lock_address   = "http://localhost:8000/state_identifier/lock"
    unlock_address = "http://localhost:8000/state_identifier/unlock"
    # Optional: (Authentication token if implemented or any other required headers)
  }
}

resource "random_id" "example" {
  byte_length = 8
}
