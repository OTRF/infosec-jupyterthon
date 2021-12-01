# What is Docker
Docker is an open platform for developing, shipping, and running application.Docker allow you to deploy development environment with consistent package dependecies across multiple workstations.
More Information about Docker : [Docker Docs](https://docs.docker.com/get-started/overview/)

# Installation
Docker Desktop is an easy-to-install application for your Mac or Windows environment that enables you to build and share containerized applications and microservices. Docker Desktop includes the Docker daemon (dockerd), the Docker client (docker), Docker Compose, Docker Content Trust, Kubernetes, and Credential Helper. 

- Download and Install Docker 
    - [Docker for Windows](https://hub.docker.com/editions/community/docker-ce-desktop-windows) 
    - [Docker Desktop for Mac (macOS)](https://docs.docker.com/desktop/mac/install/)
- Double click `Docker for Windows Installer` to run the installer
- When the installation finishes, docker starts automatically. The whale icon in the notification area indicates that Docker is running, and accessible from a terminal.
- Open a command-line terminal like PowerShell, and try out some Docker commands!
- Run `docker version` to check the version.
- Run `docker run hello-world` to verify that Docker can pull and run images.

# How to start/run Docker Image

 - Pull OTRF\Jupyterthon image from Docker directly.
`docker run -p 8888:8888 -e JUPYTER_ENABLE_LAB=yes otrf/jupyterthon` 

The following works with a relative path to an image into a subfolder next to the document:

<img src="./docs/images/rundockerimage.png" alt="Screenshot showing docker image pull and run">

- Copy and paste the link into your web browser.
_ you will see Jupyterhub UI.

 - You can also build DockerImage locally with the Dockerfile. Clone the OTRF/jupyterthon repo.
 
    `git clone https://github.com/OTRF/infosec-jupyterthon.git`
 - Navigate to the repo directory.
 - Run the command to build the image
    `docker build -t <name for image> .`


# How to attach Docker Image to VS Code
- Install Docker extension for VS Code from extension tab.
- Press `Ctrl+Shift+P` to go to command pallett and type **Remote-Containers: Attach to Running Container**
- select container running on your host.
- You will see in the bottom left the container attached.

    <img src="./docs/images/vscode-docker.png" alt="Screenshot showing docker image pull and run">

- For more information, check VS Code Docs [Developing inside a container](https://code.visualstudio.com/docs/remote/containers)



