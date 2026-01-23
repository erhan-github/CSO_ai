package main

import "fmt"

type Database struct {
    URI string
}

type Storage interface {
    Save(data string) error
}

func (db *Database) Save(data string) error {
    fmt.Printf("Saving to %s: %s\n", db.URI, data)
    return nil
}

func Connect(uri string) *Database {
    return &Database{URI: uri}
}
