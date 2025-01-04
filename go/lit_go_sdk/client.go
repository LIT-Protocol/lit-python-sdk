package lit_go_sdk

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"
	"time"
)

// LitClient represents the main client for interacting with the Lit SDK
type LitClient struct {
	port   int
	server *NodeServer
}

// NewLitClient creates a new instance of LitClient
func NewLitClient() (*LitClient, error) {
	port := 3092
	client := &LitClient{
		port: port,
	}

	// Check if server is already running
	if !client.isServerRunning() {
		server := NewNodeServer(port)
		if err := server.Start(); err != nil {
			return nil, fmt.Errorf("failed to start server: %w", err)
		}
		client.server = server

		if err := client.waitForServer(10 * time.Second); err != nil {
			server.Stop()
			return nil, err
		}
	}

	return client, nil
}

// isServerRunning checks if the Node.js server is already running
func (c *LitClient) isServerRunning() bool {
	resp, err := http.Post(fmt.Sprintf("http://localhost:%d/isReady", c.port), "application/json", nil)
	if err != nil {
		return false
	}
	defer resp.Body.Close()

	var result map[string]interface{}
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return false
	}

	return result["ready"] == true
}

// waitForServer waits for the server to become available
func (c *LitClient) waitForServer(timeout time.Duration) error {
	deadline := time.Now().Add(timeout)
	for time.Now().Before(deadline) {
		if c.isServerRunning() {
			return nil
		}
		time.Sleep(100 * time.Millisecond)
	}
	return fmt.Errorf("server failed to start within timeout period")
}

// SetAuthToken sets the auth token on the Node.js server
func (c *LitClient) SetAuthToken(authToken string) (map[string]interface{}, error) {
	payload := map[string]string{"authToken": authToken}
	return c.post("/setAuthToken", payload)
}

// ExecuteJS executes JavaScript code on the Node.js server
func (c *LitClient) ExecuteJS(code string) (map[string]interface{}, error) {
	payload := map[string]string{"code": code}
	return c.post("/executeJs", payload)
}

// CreateWallet creates a new wallet on the Node.js server
func (c *LitClient) CreateWallet() (map[string]interface{}, error) {
	return c.post("/createWallet", nil)
}

// GetPKP gets the PKP from the Node.js server
func (c *LitClient) GetPKP() (map[string]interface{}, error) {
	resp, err := http.Get(fmt.Sprintf("http://localhost:%d/pkp", c.port))
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	var result map[string]interface{}
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return nil, err
	}
	return result, nil
}

// Sign signs a message with a PKP
func (c *LitClient) Sign(toSign string) (map[string]interface{}, error) {
	payload := map[string]string{"toSign": toSign}
	return c.post("/sign", payload)
}

// post is a helper function to make POST requests
func (c *LitClient) post(endpoint string, payload interface{}) (map[string]interface{}, error) {
	var body bytes.Buffer
	if payload != nil {
		if err := json.NewEncoder(&body).Encode(payload); err != nil {
			return nil, err
		}
	}

	resp, err := http.Post(
		fmt.Sprintf("http://localhost:%d%s", c.port, endpoint),
		"application/json",
		&body,
	)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	var result map[string]interface{}
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return nil, err
	}
	return result, nil
}

// Close stops the Node.js server if it was started by this client
func (c *LitClient) Close() error {
	if c.server != nil {
		return c.server.Stop()
	}
	return nil
}
