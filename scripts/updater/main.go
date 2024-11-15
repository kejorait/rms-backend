package main

import (
	"archive/zip"
	"encoding/json"
	"fmt"
	"io"
	"io/ioutil"
	"log"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
)

// GitHubRelease holds GitHub API response for releases
type GitHubRelease struct {
	TagName string `json:"tag_name"`
	Assets  []struct {
		Name               string `json:"name"`
		BrowserDownloadURL string `json:"browser_download_url"`
	} `json:"assets"`
}

// Unzip extracts a zip file to the specified destination directory.
func Unzip(zipPath, targetDir string) error {
	// Open the ZIP file
	r, err := zip.OpenReader(zipPath)
	if err != nil {
		return fmt.Errorf("failed to open zip file: %w", err)
	}
	defer r.Close()

	// Ensure the target directory exists
	if err := os.MkdirAll(targetDir, 0755); err != nil {
		return fmt.Errorf("failed to create target directory: %w", err)
	}

	// Iterate through files in the ZIP archive
	for _, f := range r.File {
		// Skip directories or files without a "/"
		if !strings.Contains(f.Name, "/") {
			continue
		}

		// Remove the first directory from the path
		trimmedPath := strings.Join(strings.SplitN(f.Name, "/", 2)[1:], "/")
		if trimmedPath == "" {
			continue
		}

		// Resolve the full path to extract
		fullPath := filepath.Join(targetDir, trimmedPath)

		// Check if it's a directory
		if f.FileInfo().IsDir() {
			if err := os.MkdirAll(fullPath, f.Mode()); err != nil {
				return fmt.Errorf("failed to create directory %s: %w", fullPath, err)
			}
			continue
		}

		// Extract the file
		if err := extractFile(f, fullPath); err != nil {
			return fmt.Errorf("failed to extract file %s: %w", fullPath, err)
		}
	}

	return nil
}

func extractFile(f *zip.File, destPath string) error {
	// Open the file inside the ZIP archive
	rc, err := f.Open()
	if err != nil {
		return err
	}
	defer rc.Close()

	// Ensure the directory for the file exists
	if err := os.MkdirAll(filepath.Dir(destPath), 0755); err != nil {
		return err
	}

	// Create the destination file
	destFile, err := os.OpenFile(destPath, os.O_WRONLY|os.O_CREATE|os.O_TRUNC, f.Mode())
	if err != nil {
		return err
	}
	defer destFile.Close()

	// Copy the file contents
	_, err = io.Copy(destFile, rc)
	return err
}

// getFileVersion fetches the version of the binary
func getFileVersion(filePath string) (string, error) {
	cmd := exec.Command("powershell", "-Command", fmt.Sprintf("(Get-Item '%s').VersionInfo.ProductVersion", filePath))
	output, err := cmd.CombinedOutput()
	if err != nil {
		return "0.0.0", err
	}

	trimmedOutput := strings.TrimSpace(string(output))
	if strings.Contains(trimmedOutput, "Cannot") {
		return "0.0.0", nil
	}

	return "v" + trimmedOutput, nil
}

// getFileVersionZip finds the version information from version.txt in a folder with the same name as the .zip file
func getFileVersionZip(zipPath string) (string, error) {
	// Ensure the path is to a .zip file
	if filepath.Ext(zipPath) != ".zip" {
		return "0.0.0", fmt.Errorf("file is not a .zip archive")
	}

	// Get the base name (without extension) of the .zip file
	baseName := strings.TrimSuffix(filepath.Base(zipPath), ".zip")
	folderPath := filepath.Join(filepath.Dir(zipPath), baseName, "static")

	// Check if the folder with the same name exists
	if _, err := os.Stat(folderPath); os.IsNotExist(err) {
		return "", fmt.Errorf("directory %s not found", folderPath)
	}

	// Locate the version.txt file inside the folder
	versionFilePath := filepath.Join(folderPath, "version.txt")
	versionData, err := ioutil.ReadFile(versionFilePath)
	if err != nil {
		return "", fmt.Errorf("failed to read version.txt: %v", err)
	}

	// Trim any whitespace or newline characters
	return strings.TrimSpace(string(versionData)), nil
}

// getAllGitHubReleases retrieves all release versions from GitHub
func getAllGitHubReleases(owner string, repo string) ([]GitHubRelease, error) {
	url := fmt.Sprintf("https://api.github.com/repos/%s/%s/releases", owner, repo)
	resp, err := http.Get(url)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	var releases []GitHubRelease
	if err := json.NewDecoder(resp.Body).Decode(&releases); err != nil {
		return nil, err
	}

	return releases, nil
}

// downloadFile downloads a file from the URL to the specified path
func downloadFile(url, filePath string) error {
	// Ensure the directory exists
	dir := filepath.Dir(filePath)
	if err := os.MkdirAll(dir, os.ModePerm); err != nil {
		return fmt.Errorf("failed to create directory: %v", err)
	}

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

// getExecUrlAndDownload attempts to download and replace the executable
func getExecUrlAndDownload(release GitHubRelease, currentExePath, newExePath string) {
	fmt.Println("A newer version is available. Downloading update...")

	var downloadURL string
	for _, asset := range release.Assets {
		if filepath.Base(asset.Name) == filepath.Base(currentExePath) {
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
}

// checkAndUpdate iterates over each release, finds a matching executable, and updates if needed
func checkAndUpdate(currentExePath, newExePath string, owner string, repo string) {
	releases, err := getAllGitHubReleases(owner, repo)
	if err != nil {
		log.Fatalf("Error fetching GitHub releases: %v", err)
	}

	fmt.Println("\nCurrent executable:", currentExePath)

	// Get local version
	localVersion := ""
	if filepath.Ext(currentExePath) == ".exe" {
		localVersion, err = getFileVersion(currentExePath)
		if err != nil {
			fmt.Println("Local version not found, downloading the latest executable.")
			localVersion = "0.0.0"
		}
	} else if filepath.Ext(currentExePath) == ".zip" {
		localVersion, err = getFileVersionZip(currentExePath)
		if err != nil {
			fmt.Println("Local version not found, downloading the latest zip.")
			localVersion = "0.0.0"
		}
	} else {
		fmt.Println("Invalid file extension")
	}

	fmt.Println("\nCurrent version:", localVersion)

	// Iterate over all releases and check for a matching executable in each release
	for _, release := range releases {
		fmt.Println("\nChecking release:", release.TagName)
		fmt.Printf("\nRelease %s > Local %s: %t", release.TagName[1:], localVersion, release.TagName[1:] > localVersion)
		if release.TagName[1:] > localVersion {
			for _, asset := range release.Assets {
				fmt.Print("\nChecking asset: ", asset.Name)
				if filepath.Base(asset.Name) == filepath.Base(currentExePath) {
					fmt.Printf("\nNewer version found: %s\n", release.TagName)
					getExecUrlAndDownload(release, currentExePath, newExePath)
					if filepath.Ext(currentExePath) == ".zip" {
						basePath := strings.TrimSuffix(filepath.Base(currentExePath), ".zip")
						dir := filepath.Join("fe", basePath)
						Unzip(currentExePath, dir)
						// delete the zip file
						os.Remove(currentExePath)
					}

					return
				}
			}
		}
	}
	fmt.Println("\nNo update needed. The current version is up-to-date.")
}

// main checks for updates and replaces the old binary if a new version is found
func main() {
	var backendExePath = "./be/rms-backend.exe"
	var newBackendExePath = "./be/rms-backend_new.exe"

	owner := "mliem2k"
	repo := "rms-backend"

	// Check for backend executable updates
	checkAndUpdate(backendExePath, newBackendExePath, owner, repo)

	backendExePath = "./be/serial_runner.exe"
	newBackendExePath = "./be/serial_runner_new.exe"

	// Check for backend executable updates
	checkAndUpdate(backendExePath, newBackendExePath, owner, repo)

	backendExePath = "./fe/rms-frontend.exe"
	newBackendExePath = "./fe/rms-frontend_new.exe"

	checkAndUpdate(backendExePath, newBackendExePath, owner, repo)

	owner = "kejorait"
	repo = "rms-releases"

	backendExePath = "./fe/employee.zip"
	newBackendExePath = "./fe/employee_new.zip"

	checkAndUpdate(backendExePath, newBackendExePath, owner, repo)

	backendExePath = "./fe/admin.zip"
	newBackendExePath = "./fe/admin_new.zip"

	checkAndUpdate(backendExePath, newBackendExePath, owner, repo)
}
