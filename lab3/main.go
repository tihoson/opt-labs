package main

import (
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
)

func main() {
	for {
		var url, path string
		fmt.Scan(&url, &path)
		go worker(url, path)
	}
}

func worker(url, path string) {
	out, err := os.Create(path)
	if err != nil {
		log.Println(err)
	}
	defer out.Close()

	resp, err := http.Get(url)
	if err != nil {
		log.Println(err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		log.Println(resp.StatusCode)
	}

	_, err = io.Copy(out, resp.Body)
	if err != nil {
		log.Println(err)
	}
	fmt.Println(path, " done")
}
