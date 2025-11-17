# Ubuntu Environment Setup Guide

> ⚠️ **NOTE**  
> You may use **any package manager** or install each tool manually from their official installation instructions.  
> The steps below use `apt` as an example and are **verified** to work with this project.
>
> ✅ The project has been tested and is known to work with:
> - **Java**: version `11.*`
> - **Python**: version `3.13.*+`
> - **Spark**: version `3.5.*+`
>
> ⚠️ We do **not guarantee** project stability with other versions of these applications.

⚠️⚠️⚠️ The software mentioned below is **approved by company policy**.  
If you decide to use alternative tools (e.g., **Docker Desktop** instead of **Rancher Desktop**), we highly recommend reviewing the list of allowed software in the internal knowledge base:  
[Approved Freeware](https://kb.epam.com/display/public/EPMSAM/Approved+Freeware)

This guide will help you configure your Ubuntu 24.10 development environment.

---

## Step 1: Update Package Lists

Open the **Terminal** and run:

```bash
sudo apt update && sudo apt upgrade -y
```

Once the upgrade completes, ensure `curl` is installed:

```bash
sudo apt install -y curl
```

---

## Step 2: Install Required Tools with `apt`

In the Terminal, run the following commands to install the required tools:

```bash
sudo apt install -y \
    openjdk-11-jdk \
    maven \
    python3 \
    python3-pip \
    git \
    dos2unix
```

> 💡 **Note:** `azure-cli`, `helm`, `terraform`, and `kubectl` are installed via their official repositories (see below).

### Add Azure CLI Repository:

```bash
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
```

### Add Terraform Repository:

```bash
curl -fsSL https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list
sudo apt update && sudo apt install terraform
```

### Add Helm Repository:

```bash
curl https://baltocdn.com/helm/signing.asc | sudo apt-key add -
sudo apt install apt-transport-https --yes
echo "deb https://baltocdn.com/helm/stable/debian/ all main" | sudo tee /etc/apt/sources.list.d/helm-stable-debian.list
sudo apt update && sudo apt install helm
```

### Install `kubectl` (Kubernetes CLI):

```bash
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
kubectl version --client
```

---

## Step 3: Install Rancher Desktop

Please refer to the official Rancher Desktop installation guide for Linux before proceeding to ensure you follow the latest recommended steps and system requirements:

- 📄 [Rancher Desktop Installation Documentation](https://docs.rancherdesktop.io/getting-started/installation/)

Once you've reviewed the official guide:

1. Add the Rancher Desktop repository and install via the following commands:

```bash
curl -s https://download.opensuse.org/repositories/isv:/Rancher:/stable/deb/Release.key | gpg --dearmor | sudo dd status=none of=/usr/share/keyrings/isv-rancher-stable-archive-keyring.gpg

echo 'deb [signed-by=/usr/share/keyrings/isv-rancher-stable-archive-keyring.gpg] https://download.opensuse.org/repositories/isv:/Rancher:/stable/deb/ ./' | sudo dd status=none of=/etc/apt/sources.list.d/isv-rancher-stable.list

sudo apt update
sudo apt install rancher-desktop
```

3. Launch **Rancher Desktop** and ensure Docker support is enabled.

---

## Step 4: Verify Docker CLI Availability

In the Terminal, run:

```bash
docker -v
```

If the Docker version is printed, everything is working.  
If not, restart Rancher Desktop and verify it’s configured to provide the Docker CLI.

---

## Step 5: Install Apache Spark

We recommend installing Apache Spark by following the official instructions, which provide multiple options depending on your system and requirements.

- 📄 [Getting Started with PySpark – Manual Download Instructions](https://spark.apache.org/docs/latest/api/python/getting_started/install.html#manually-downloading)
- 📦 [Apache Spark Downloads Page](https://spark.apache.org/downloads.html)

> ⚠️ **Note:** You are free to use any version or method of installation that works for your setup, but this project was tested with **Spark 3.5.\***.

---

## ✅ You’re All Set

Once all tools are installed and Rancher Desktop is running, you’re ready to move on with the project setup.
