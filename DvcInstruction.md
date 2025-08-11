# 🚀 Push Data to Google Drive using DVC + Service Account

> ✅ Works even when Google blocks DVC’s default OAuth  
> 🛠️ Tested on Windows PowerShell and Linux/macOS

---

## 🧱 Prerequisites

- Python installed
- Git and DVC installed
- Google Cloud account
- Google Drive folder or Shared Drive

---

## 📦 1. Install DVC with Google Drive support

```bash
pip install "dvc[gdrive]"
```

## 🧑‍💻 2. Initialize DVC in your project (if not already)

```bash
cd your-project-folder
dvc init
git add .dvc .gitignore
git commit -m "Initialize DVC"
```

## 🗃️ 3. Track Your Data with DVC
```bash
git rm -r --cached data/
dvc add data/
git add data.dvc .gitignore
git commit -m "Track data with DVC"
```
## ☁️ 4. Create a Shared Drive on Google Drive

1. Navigate to [Google Shared Drives](https://drive.google.com/drive/shared-drives)
2. Click **New** → Enter a name (e.g., `DVC Storage`)
3. After creation, copy the Shared Drive ID from the URL:
```
https://drive.google.com/drive/u/0/folders/0AAbCDEFghIJKLmnoP
                                  ↑ Shared Drive ID = 0AAbCDEFghIJKLmnoP
```
## 🔐 5. Create a Google Service Account
1. Go to: [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (e.g., dvc-drive-project)
3. Enable Google Drive API:
- Go to APIs & Services > Library
- Search for "Google Drive API" → Enable it
4. Go to ```IAM & Admin > Service Accounts```
5. Click **Create Service Account**
6. After creation, go to **Keys > Add Key > JSON**
7. Download the ```.json``` key (e.g., ```dvc-sa-key.json```)

## 🤝 6. Share the Shared Drive with the Service Account
1. Go to your Shared Drive
2. Click its name → “Manage members”
3. Add the service account email (from the JSON file):
```
dvc-sa@your-project.iam.gserviceaccount.com
```
4. Grant **Content Manager** or **Manager** access

## 🔗 7. Configure DVC Remote
```bash
dvc remote add -d gdrive_remote gdrive://<SHARED_DRIVE_ID>
dvc remote modify gdrive_remote gdrive_use_service_account true
dvc remote modify gdrive_remote gdrive_service_account_json_file_path ./dvc-sa-key.json
```
>📌 Replace ```<SHARED_DRIVE_ID>``` and ```./dvc-sa-key.json``` with your values

## ☁️ 8. Push Data to Google Drive
```bash
dvc push
```

## 😁 9. Tracking Dataset change
```bash
dvc add data
git add data.dvc
git commit -m "Update dataset"
dvc push
```

# ✅ Summary of Key Commands
```bash
pip install "dvc[gdrive]"
dvc init
git rm -r --cached data/
dvc add data/
git add data.dvc .gitignore
git commit -m "Track data"
dvc remote add -d gdrive_remote gdrive://<SHARED_DRIVE_ID>
dvc remote modify gdrive_remote gdrive_use_service_account true
dvc remote modify gdrive_remote gdrive_service_account_json_file_path ./dvc-sa-key.json
dvc push
```



