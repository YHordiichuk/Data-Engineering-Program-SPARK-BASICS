# macOS Environment Setup Guide

> ⚠️ **NOTE**  
> You may use **any package manager** or install each tool manually from their official installation instructions.  
> The steps below use [Homebrew](https://brew.sh/) as an example and are **verified** to work with this project.
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

This guide will help you configure your macOS development environment.

---

## Step 1: Install Homebrew (Package Manager)

1. Open the **Terminal**.
2. Run the following command (official Homebrew install script):

   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```

3. Follow the instructions in the terminal. It may ask for your password.
4. After installation, add Homebrew to your shell profile:

For Zsh (default shell on macOS Catalina+):

   ```bash
   echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
   eval "$(/opt/homebrew/bin/brew shellenv)"
   ```

For Bash:

   ```bash
   echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.bash_profile
   eval "$(/opt/homebrew/bin/brew shellenv)"
   ```

## Step 2: Install Required Tools with Homebrew

In your Terminal, run the following command to install all the required tools:

   ```bash
   brew install \
        rancher \
        openjdk@11 \
        azure-cli \
        maven \
        terraform \
        python \
        git \
        dos2unix \
        helm \
        kubectl \
        eksctl
   ```

💡 Note: `openjdk@11` may require setting your `JAVA_HOME`. You can add the following to your shell profile:

   ```bash
    export PATH="/opt/homebrew/opt/openjdk@11/bin:$PATH"
    export CPPFLAGS="-I/opt/homebrew/opt/openjdk@11/include"
    export JAVA_HOME="$(/usr/libexec/java_home -v11)"
   ```

## Step 3: Verify Docker CLI Availability

Make sure Rancher Desktop is running and provides Docker support.

In the Terminal, run:

   ```bash
   docker -v
   ```

If the Docker version is printed, everything is working.
If not, restart Rancher Desktop and verify it’s configured to provide the Docker CLI.

## Step 4: Install Apache Spark

We recommend installing Apache Spark by following the official instructions, which provide multiple options depending on your system and requirements.

- 📄 [Getting Started with PySpark – Manual Download Instructions](https://spark.apache.org/docs/latest/api/python/getting_started/install.html#manually-downloading)
- 📦 [Apache Spark Downloads Page](https://spark.apache.org/downloads.html)

> ⚠️ **Note:** You are free to use any version or method of installation that works for your setup, but this project was tested with **Spark 3.5.\***.

✅ You’re All Set

Once all tools are installed and Rancher Desktop is running, you’re ready to move on with the project setup.
