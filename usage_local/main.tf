terraform {
 
  backend "http" {
    address        = "http://localhost:8080/state_identifier"
    lock_address   = "http://localhost:8080/state_identifier/lock"
    unlock_address = "http://localhost:8080/state_identifier/unlock"
    headers = {
      X-API-Token = "managing-opentofu-state-secure-api-token"
    }
  }
}

resource "random_id" "example" {
  byte_length = 8
}
