package main

import (
	"archive/zip"
	"bufio"
	"encoding/json"
	"fmt"
	"io"
	"io/ioutil"
	"log"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"
	"strconv"
	"strings"

	"github.com/schollz/progressbar/v3"
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

// downloadFile downloads a file from the URL to the specified path with a progress bar.
func downloadFile(url, filePath string) error {
	// Ensure the directory exists
	dir := filepath.Dir(filePath)
	if err := os.MkdirAll(dir, os.ModePerm); err != nil {
		return fmt.Errorf("failed to create directory: %v", err)
	}

	// Get the response from the URL
	resp, err := http.Get(url)
	if err != nil {
		return err
	}
	defer resp.Body.Close()

	// Create the destination file
	file, err := os.Create(filePath)
	if err != nil {
		return err
	}
	defer file.Close()

	// Create the progress bar
	bar := progressbar.NewOptions(int(resp.ContentLength),
		progressbar.OptionSetWidth(50),
		progressbar.OptionSetDescription("Downloading"),
		progressbar.OptionSetPredictTime(true),
	)

	// Use TeeReader to copy the content to both the file and the progress bar
	_, err = io.Copy(io.MultiWriter(file, bar), resp.Body)
	if err != nil {
		return err
	}

	return nil
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

	// Download the latest binary with a progress bar
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
		releaseVersion := release.TagName[1:] // Remove 'v'
		localVersionNum := localVersion[1:]
		fmt.Printf("\nRelease %s > Local %s: %t", releaseVersion, localVersionNum, compareVersions(releaseVersion, localVersionNum))
		if releaseVersion > localVersionNum {
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
func compareVersions(version1, version2 string) bool {
	v1Parts := strings.Split(version1, ".")
	v2Parts := strings.Split(version2, ".")

	for i := 0; i < len(v1Parts) && i < len(v2Parts); i++ {
		v1, _ := strconv.Atoi(v1Parts[i])
		v2, _ := strconv.Atoi(v2Parts[i])
		if v1 > v2 {
			return true
		} else if v1 < v2 {
			return false
		}
	}
	return false
}
func askForUpdate(prompt string) string {
	reader := bufio.NewReader(os.Stdin)
	fmt.Printf("%s (yes/no): ", prompt)
	input, _ := reader.ReadString('\n')
	input = strings.TrimSpace(strings.ToLower(input))
	if input == "all" || input == "a" {
		return "a"
	}
	if input == "yes" || input == "y" {
		return "y"
	}
	if input == "only" || input == "o" {
		return "o"
	}
	return "n"
}

func main() {
	owner := "mliem2k"
	repo := "rms-backend"

	updateAll := askForUpdate("Update all executables and zips?")

	response := askForUpdate("Update backend executable (rms-backend.exe)?")
	if updateAll == "a" || response == "y" || response == "o" {
		checkAndUpdate("./be/rms-backend.exe", "./be/rms-backend_new.exe", owner, repo)
		if response == "o" {
			return // Stop further updates after one update
		}
	}

	// Ask about serial runner executable update
	if updateAll == "a" || askForUpdate("Update serial runner executable (serial_runner.exe)?") == "y" || askForUpdate("Update serial runner executable (serial_runner.exe)?") == "o" {
		checkAndUpdate("./be/serial_runner.exe", "./be/serial_runner_new.exe", owner, repo)
		if response == "o" {
			return // Stop further updates after one update
		}
	}

	// Ask about frontend executable update
	if updateAll == "a" || askForUpdate("Update frontend executable (rms-frontend.exe)?") == "y" || askForUpdate("Update frontend executable (rms-frontend.exe)?") == "o" {
		checkAndUpdate("./fe/rms-frontend.exe", "./fe/rms-frontend_new.exe", owner, repo)
		if response == "o" {
			return // Stop further updates after one update
		}
	}

	// Switch to another repository
	owner = "kejorait"
	repo = "rms-releases"

	// Ask about employee zip update
	if updateAll == "a" || askForUpdate("Update employee zip (employee.zip)?") == "y" || askForUpdate("Update employee zip (employee.zip)?") == "o" {
		checkAndUpdate("./fe/employee.zip", "./fe/employee_new.zip", owner, repo)
		if response == "o" {
			return // Stop further updates after one update
		}
	}

	// Ask about admin zip update
	if updateAll == "a" || askForUpdate("Update admin zip (admin.zip)?") == "y" || askForUpdate("Update admin zip (admin.zip)?") == "o" {
		checkAndUpdate("./fe/admin.zip", "./fe/admin_new.zip", owner, repo)
		if response == "o" {
			return // Stop further updates after one update
		}
	}

	// Ask about customer zip update
	if updateAll == "a" || askForUpdate("Update customer zip (customer.zip)?") == "y" || askForUpdate("Update customer zip (customer.zip)?") == "o" {
		checkAndUpdate("./fe/customer.zip", "./fe/customer_new.zip", owner, repo)
		if response == "o" {
			return // Stop further updates after one update
		}
	}
}
