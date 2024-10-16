# Image Upload and Gallery App

Welcome to the Image Upload and Gallery App! This project serves as a testing ground for the Azure Web App, demonstrating the capabilities of running Python Flask applications, managing file downloads and uploads, and leveraging Azure Web App storage, with plans to integrate Azure Blob Storage later. Enhanced by AI, this app provides a seamless and efficient way to handle images.

## Features

- **Image Upload**: Upload images in various formats (png, jpg, jpeg, gif).
- **Image Gallery**: Browse through uploaded images with detailed information like size and upload time.
- **Batch Delete**: Select and delete multiple images at once.
- **Real-time Information**: View server and file modification times in real-time.

## Tech Stack

- **Backend**: Flask (Python)
- **Frontend**: HTML, CSS, JavaScript, Bootstrap, Axios
- **Image Processing**: PIL (Python Imaging Library)
- **Deployment**: Azure Web Apps

## Installation

1. **Clone the repository**:

   ```sh
   git clone https://github.com/oreing/images_upload.git
   cd images_upload
   ```

2. **Create a virtual environment**:

   ```sh
   python3 -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install dependencies**:

   ```sh
   pip install -r requirements.txt
   ```

4. **Run the application**:

   - **Development**:

   ```sh
   python app.py
   ```

   - **Production**:

   ```sh
   gunicorn --bind 0.0.0.0:5000 app:app
   ```

5. **Access the app**:
   Open your web browser and go to `http://127.0.0.1:5000`.

## Configuration

Ensure the upload folder exists and is set correctly in `app.py`:

```python
UPLOAD_FOLDER = os.path.expanduser("/home/site/wwwroot/upload")
```

You can adjust the folder path based on your environment.

## Deployment to Azure

### Prerequisites

- Ensure you have the [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli) installed.
- An Azure account and subscription.

### Steps

1. **Login to Azure**:

   ```sh
   az login
   ```

2. **Create a Resource Group**:

   ```sh
   az group create --name myResourceGroup --location "East US"
   ```

3. **Create an App Service Plan**:

   ```sh
   az appservice plan create --name myAppServicePlan --resource-group myResourceGroup --sku FREE
   ```

4. **Create a Web App**:

   ```sh
   az webapp create --resource-group myResourceGroup --plan myAppServicePlan --name myWebApp
   ```

5. **Configure App Settings**:
   Set `SCM_DO_BUILD_DURING_DEPLOYMENT` to `true` to enable build during deployment.

   ```sh
   az webapp config appsettings set -g myResourceGroup -n myWebApp --settings SCM_DO_BUILD_DURING_DEPLOYMENT=true
   ```

6. **Deploy the app**:
   Ensure your application is packaged into a zip file named `app.zip`. Make sure to ignore unnecessary files.

   ```sh
   zip -r app.zip * -x "*.git*" "*venv*"
   az webapp deploy --resource-group myResourceGroup --name myWebApp --src-path app.zip --type zip
   ```

7. **Stream the logs** (optional):
   ```sh
   az webapp log tail --resource-group myResourceGroup --name myWebApp
   ```

## Troubleshooting Guide

1. **Set SCM_DO_BUILD_DURING_DEPLOYMENT to True**:
   - **Issue**: App build fails during deployment.
   - **Solution**: Ensure this setting is enabled to allow builds during deployment.
   ```sh
   az webapp config appsettings set -g myResourceGroup -n myWebApp --settings SCM_DO_BUILD_DURING_DEPLOYMENT=true
   ```

## Contributing

Feel free to fork this project and submit pull requests. We welcome all contributions!

## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.

---

Happy coding! 🎉
