package main

import (
	"flag"
	"fmt"
	"net"
	"os"
)

func main() {
	ip := os.Args[1]
	flag.Parse()

	if ip == "" {
		return
	}

	ports := []int{}
	for port := 1; port <= 65535; port++ {
		ports = append(ports, port)
	}

	fmt.Printf("Scanning %s...\n", ip)
	scanPorts(ip)

	fmt.Println("Determining services...")
	services, err := getServices(ip, ports)
	if err != nil {
		fmt.Printf("Could not determine services: %v\n", err)
	} else {
		fmt.Println("Services:")
		for port, service := range services {
			fmt.Printf("Open Port %d/TCP: %s\n", port, service)
		}
	}
}

func scanPorts(ip string) {
	for port := 1; port <= 65535; port++ {
		address := fmt.Sprintf("%s:%d", ip, port)
		conn, err := net.Dial("tcp", address)
		if err != nil {
			continue
		}
		conn.Close()

	}
}
func getServices(ip string, ports []int) (map[int]string, error) {
	services := make(map[int]string)

	for _, port := range ports {
		address := fmt.Sprintf("%s:%d", ip, port)
		conn, err := net.Dial("tcp", address)
		if err != nil {
			continue
		}
		conn.Close()

		services[port] = "Unknown"
	}

	return services, nil
}
