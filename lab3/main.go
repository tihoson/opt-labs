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
	log.Printf("---------------\nstart new job\nurl -> %s\npath\n%s\n---------------\n", url, path)

	out, err := os.Create(path)
	if err != nil {
		log.Printf("create file error: %v", err)
		return
	}
	defer out.Close()
	log.Printf("create file %s\n", path)

	resp, err := http.Get(url)
	if err != nil {
		log.Printf("http get error: %v", err)
		return
	}
	defer resp.Body.Close()
	log.Printf("response from %s for file %s received\n", url, path)

	if resp.StatusCode != http.StatusOK {
		log.Printf("http response code is %d not %d", resp.StatusCode, http.StatusOK)
		return
	}

	_, err = io.Copy(out, resp.Body)
	if err != nil {
		log.Printf("body copy error: %v", err)
		return
	}
	fmt.Printf("---------------\njob is done\nurl -> %s\npath\n%s\n---------------\n", url, path)
}
