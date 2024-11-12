package main

import (
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
)

// Constants for GitHub repo
const (
	owner = "mliem2k"
	repo  = "rms-backend"
)

// GitHubRelease holds GitHub API response
type GitHubRelease struct {
	TagName string `json:"tag_name"`
	Assets  []struct {
		Name               string `json:"name"`
		BrowserDownloadURL string `json:"browser_download_url"`
	} `json:"assets"`
}

// getFileVersion fetches the version of the binary
func getFileVersion(filePath string) (string, error) {
	cmd := exec.Command("powershell", "-Command", fmt.Sprintf("(Get-Item '%s').VersionInfo.ProductVersion", filePath))
	output, err := cmd.CombinedOutput()
	if err != nil {
		return "", err
	}
	return strings.TrimSpace(string(output)), nil
}

// getLatestGitHubVersion retrieves the latest release version from GitHub
func getLatestGitHubVersion() (GitHubRelease, error) {
	url := fmt.Sprintf("https://api.github.com/repos/%s/%s/releases/latest", owner, repo)
	resp, err := http.Get(url)
	if err != nil {
		return GitHubRelease{}, err
	}
	defer resp.Body.Close()

	var release GitHubRelease
	if err := json.NewDecoder(resp.Body).Decode(&release); err != nil {
		return GitHubRelease{}, err
	}

	return release, nil
}

// downloadFile downloads a file from the URL to the specified path
func downloadFile(url, filePath string) error {
	resp, err := http.Get(url)
	if err != nil {
		return err
	}
	defer resp.Body.Close()

	file, err := os.Create(filePath)
	if err != nil {
		return err
	}
	defer file.Close()

	_, err = io.Copy(file, resp.Body)
	return err
}

// main checks for updates and replaces the old binary if a new version is found
func main() {
	const currentExePath = "main.exe"
	const newExePath = "main_new.exe"

	// Get local version
	localVersion, err := getFileVersion(currentExePath)
	if err != nil {
		log.Fatalf("Error retrieving local version: %v", err)
	}
	fmt.Println("Current version:", localVersion)

	// Get GitHub latest release
	release, err := getLatestGitHubVersion()
	if err != nil {
		log.Fatalf("Error fetching GitHub version: %v", err)
	}
	fmt.Println("Latest GitHub version:", release.TagName)

	// Compare versions
	if release.TagName > localVersion {
		fmt.Println("A newer version is available. Downloading update...")

		var downloadURL string
		for _, asset := range release.Assets {
			if filepath.Ext(asset.Name) == ".exe" {
				downloadURL = asset.BrowserDownloadURL
				break
			}
		}

		if downloadURL == "" {
			fmt.Println("No valid executable asset found in the latest release.")
			return
		}

		// Download the latest binary
		err := downloadFile(downloadURL, newExePath)
		if err != nil {
			log.Fatalf("Error downloading file: %v", err)
		}

		// Replace the current executable with the new one
		if err = os.Rename(newExePath, currentExePath); err != nil {
			log.Fatalf("Error updating binary: %v", err)
		}
		fmt.Println("Updated the binary successfully.")
	} else {
		fmt.Println("No update needed. The current version is up-to-date.")
	}
}
