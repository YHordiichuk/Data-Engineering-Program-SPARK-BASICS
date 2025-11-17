# SparkBasics [python]

## Prerequisites

Before proceeding, ensure you have the following tools installed:

- Rancher Desktop – Required for running Kubernetes locally (alternative to Docker Desktop). Please keep it running.
- Java – Needed for running Java applications and scripts. Recommended Java version - openjdk 11.
- Python 3 – Needed for running Python-based applications and scripts. Recommended Python version - 3.13.(latest version).
- AWS CLI – Used to interact with AWS services and manage resources.
- Terraform – Infrastructure as Code (IaC) tool for provisioning AWS resources.
- Spark – Unified analytics engine for large-scale data processing; required to run Spark jobs using spark-submit.
- dos2unix - command-line tool that converts Windows-style endings (CRLF) to Unix (LF).
- eksctl – Command-line tool for creating and managing Kubernetes clusters on AWS EKS.

📘 Follow the full setup instructions for [Windows environment setup](./setup-windows.md)<br>
🍎 Follow the full setup instructions for [MacOS environment setup](./setup-macos.md)<br>
🐧 Follow the full setup instructions for [Ubuntu 24.10 environment setup](./setup-ubuntu.md)

📌 **Important Guidelines**
Please read the instructions carefully before proceeding. Follow these guidelines to avoid mistakes:

- If you see `<SOME_TEXT_HERE>`, you need to **replace this text and the brackets** with the appropriate value as described in the instructions.
- Follow the steps in order to ensure proper setup.
- Pay attention to **bolded notes**, warnings, or important highlights throughout the document.
- Clean Up AWS Resources Before Proceeding. Since you are using a **free-tier** AWS account, it’s crucial to clean up any leftover resources from previous lessons or deployments before proceeding. Free-tier accounts have strict resource quotas, and exceeding these limits may cause deployment failures.

## Prerequisites
- An active AWS account.
- Appropriate IAM permissions to create users and generate access keys (administrator access is recommended for initial setup).

## 1. AWS CLI Setup

### Log in to AWS Management Console
- Open your web browser and navigate to the [AWS Management Console](https://aws.amazon.com/console/).
- Log in using your AWS account credentials.

###  Create a New IAM User
- In the AWS Console, locate the search bar and type **IAM**, then select **IAM** from the list.
- In the left-hand navigation pane, click **Users**.

#### Create a User and Add to a Group
1. Click **Add user**.
2. Enter a  **User name**.
3. Under **Select AWS access type**, check **Programmatic access**.
4. Click **Next: Permissions**.
5. Choose **Add user to group**.
   - If a suitable group exists, select it.
   - Otherwise, create a new group by clicking **Create group**, enter a  **User group name** then assign the **AdministratorAccess** policy to the group.
6. Click **Next**.
7. Click **Create user**.

###  Retrieve Your Access Keys

- **Important:** Copy and store the **SecretAccessKey** and **AccessKeyId** immediately.
The next time you will run the command the new access key will be generated, and the old one will be deleted.
```bash
aws iam create-access-key --user-name <your-user-name>
```

### Configure the AWS CLI
- Open a terminal and run the following command:

```bash
aws configure
``` 
When prompted, enter the following details:

- **AWS Access Key ID**: Your obtained `AccessKeyId`.
- **AWS Secret Access Key**: Your obtained `SecretAccessKey`.
- **Default region name**: `us-west-1`
- **Default output format**: `json`



## 2. Deploy Infrastructure with Terraform

To start the deployment using Terraform scripts, you need to navigate to the `terraform` folder.

```bash
cd terraform/
```

Run the following Terraform commands:

```bash
terraform init
```  

```bash
terraform plan -out terraform.plan
```  

```bash
terraform apply terraform.plan
```  

## 3. AWS ECR Setup
Create a new ECR repository in AWS. This repository will be used to store the Docker image for your Spark application.

### Create an ECR Repository

To create a new ECR repository, run the following command:

```bash
aws ecr create-repository --repository-name spark-python-06
```

### Authenticate Docker to ECR
To authenticate Docker to your ECR registry, run the following commands:

1. Retrieve the authentication password
```bash
$password = aws ecr get-login-password --region <region>
```

2. Retrieve the **aws-account-id**
```bash
aws sts get-caller-identity --query "Account" --output text
```

3. Authenticate Docker to ECR
```bash
docker login --username AWS --password $password <aws-account-id>.dkr.ecr.<region>.amazonaws.com
```



## 4. Setup local project

1. Setup Python virtual environment (name it `venv`):
> Depending on your OS or Python setup, the command could be `python` or `python3`.
> You can check which is available by running:
>
> ```bash
> python --version
> ```
> or
>
> ```bash
> python3 --version
> ```

To create the virtual environment, navigate into `git root` directory and run a command:

```bash
python3 -m venv venv
```

or

```bash
python -m venv venv
```

2. activate python env


    <details>
    <summary><code>Linux</code>, <code>MacOS</code> (<i>click to expand</i>)</summary>

    ```bash
    source venv/bin/activate
    ```

    </details>
    <details>
    <summary><code>Windows - [powershell]</code> (<i>click to expand</i>)</summary>

    ```bash
    venv\Scripts\Activate.ps1
    ```

    </details>

3. Setup needed requirements into your env:

```bash
pip install -r requirements.txt
```

4. Add your code in `src/main/python/`
5. Add and Run UnitTests into folder `src/tests/`
6. Package your artifacts (new .egg file will be created under `docker/dist/`):

```bash
python3 setup.py bdist_egg
```

7. ⚠️  To build the Docker image, choose the correct command based on your CPU architecture (The first time you run this command, it may take up to 60 minutes.):

    <details>
    <summary><code>Linux</code>, <code>Windows</code>, <code>&lt;Intel-based macOS&gt;</code> (<i>click to expand</i>)</summary>

    >⚠️ Make sure `entrypoint.sh` uses LF (Unix-style) line endings. Windows-style CRLF may cause issues when running the script in a Unix-based environment. 
    If the command below doesn't work, you may need to change the line endings manually in your IDE (e.g. switch from CRLF to LF in your IDE).

    ```bash
    dos2unix.exe .\docker\*.sh
    ```
  
    then

    ```bash
    docker build -t m06-spark-image -f docker/Dockerfile docker/ --build-context extra-source=./
    ```

    </details>
    <details>
    <summary><code>macOS</code> with <code>M1/M2/M3</code> <code>&lt;ARM-based&gt;</code>  (<i>click to expand</i>)</summary>

    ```bash
    docker build --platform linux/amd64 -t m06-spark-image -f docker/Dockerfile docker/ --build-context extra-source=./
    ```

    </details>

8. Local testing (Optional)
- Setup local project before push image to ACR, to make sure if everything goes well:

    <details>
    <summary><code>Linux</code>, <code>Windows</code>, <code>&lt;Intel-based macOS&gt;</code> (<i>click to expand</i>)</summary>

    ```bash
    docker run --rm -it m06-spark-image spark-submit --master "local[*]" --py-files PATH_TO_YUR_EGG_FILE.egg /PATH/TO/YOUR/Python.py
    ```

    </details>
    <details>
    <summary><code>macOS</code> with <code>M1/M2/M3</code> <code>&lt;ARM-based&gt;</code>  (<i>click to expand</i>)</summary>

    <strong>Important Note for macOS (M1/M2/M3) Users</strong>

    When building the Docker image with the --platform linux/amd64 flag on macOS with Apple Silicon (ARM-based chips), the
    resulting image will be designed for x86_64 architecture (amd64). This is necessary because the image is meant for deployment
    in a Kubernetes cluster running on amd64 nodes.

    However, this also means that running the image locally using docker run without emulation will likely fail due to an architecture mismatch.
    Solution:
    you can build a separate ARM64 version of the image specifically for local testing using:

    ```bash
    docker build -t m06-spark-image -f docker/Dockerfile docker/ --build-context extra-source=./ 
    ```
  
    Then, run the ARM64 version locally:

    ```bash
    docker run --rm -it m06-spark-image spark-submit --master "local[*]" --py-files PATH_TO_YOUR_EGG_FILE.egg /PATH/TO/YOUR/Python.py
    ```

    </details>

Warning! (Do not forget to clean output folder, created by spark job after local testing)!

9. Tag Docker Image:

```bash
docker tag m06-spark-image:latest <aws-account-id>.dkr.ecr.<region>.amazonaws.com/spark-python-06:latest
```

10. Push Docker Image to ECR:

```bash
docker push <aws-account-id>.dkr.ecr.<region>.amazonaws.com/spark-python-06:latest
```  

11. Verify Image in ECR:

```bash
aws ecr describe-images --repository-name spark-python-06 --region <region> --query 'imageDetails[?imageTags[0]==`latest`]' --output table
```  

- **region**: The AWS region where the ECR repository is located.

## 5. Kubernetes Service Account Setup for Spark


1. Get the  cluster_name  
```bash 
aws eks list-clusters --region <region>
```

2. Update kubeconfig for the EKS cluster:
```bash
aws eks update-kubeconfig --name <cluster_name> --region <region>
```

3. Create a Service Account:
```bash
kubectl create serviceaccount spark
```


4. Create IAM Service Account for Spark
```bash
eksctl create iamserviceaccount --name spark --namespace default --cluster <cluster_name> --attach-policy-arn arn:aws:iam::<aws-account-id>:policy/S3SparkAccessPolicy --approve --override-existing-serviceaccounts
```

5. From root directory run the following command to create a ClusterRoleBinding for the Service Account:
```bash
cd spark_config
```


6. Apply the Role manifest that defines the permissions for the spark service account:
```bash
kubectl apply -f spark-role.yaml
```

7. Bind the previously created Role to the spark service account using a RoleBinding:
```bash
kubectl apply -f spark-rolebinding.yaml
```

## 6. Launch Spark app in cluster mode


1. To get cluster name, run the following command:
```bash
aws eks list-clusters --region <region>
```
2. To get the eks cluster endpoint, run the following command:
```bash
aws eks describe-cluster --region <region> --name <cluster-name> --query "cluster.endpoint" --output text
 ```
Replace:

- **<cluster-name>** with the name of your EKS cluster.
- **<region>**  with the appropriate AWS region. 

3. Get bucket name:
```bash
aws s3api list-buckets --query "Buckets[].Name" --output text
```

4. Then procceed with `spark-submit` configuration (before execute this command, update the placeholders):


  <details>
  <summary><code>Linux</code>, <code>MacOS</code>  (<i>click to expand</i>)</summary>

  ```bash
  spark-submit \
    --master k8s://https://<eks-cluster-endpoint> \
    --deploy-mode cluster \
    --name sparkbasics \
    --conf spark.kubernetes.container.image=<aws-account-id>.dkr.ecr.<region>.amazonaws.com/spark-python-06:latest \
    --conf spark.kubernetes.driver.request.cores=500m \
    --conf spark.kubernetes.driver.request.memory=2g \
    --conf spark.kubernetes.executor.request.memory=1g \
    --conf spark.kubernetes.executor.request.cores=500m \
    --conf spark.kubernetes.namespace=default \
    --conf spark.kubernetes.authenticate.driver.serviceAccountName=spark \
    --conf spark.kubernetes.driver.pod.name=spark-driver \
    --conf spark.kubernetes.executor.instances=1 \
    --conf spark.pyspark.python=/usr/bin/python3 \
    --conf spark.pyspark.driver.python=/usr/bin/python3 \
    --py-files local:///opt/<your-egg-file>.egg \
    local:///opt/src/main/python/<your-script>.py
  ```

  </details>
  <details>
  <summary><code>Windows [powershell]</code>  (<i>click to expand</i>)</summary>

  ```bash
  spark-submit `
    --master k8s://https://<eks-cluster-endpoint> `
    --deploy-mode cluster `
    --name sparkbasics `
    --conf spark.kubernetes.container.image=<aws-account-id>.dkr.ecr.<region>.amazonaws.com/spark-python-06:latest `
    --conf spark.kubernetes.driver.request.cores=500m `
    --conf spark.kubernetes.driver.request.memory=2g `
    --conf spark.kubernetes.executor.request.memory=1g `
    --conf spark.kubernetes.executor.request.cores=500m `
    --conf spark.kubernetes.namespace=default `
    --conf spark.kubernetes.authenticate.driver.serviceAccountName=spark `
    --conf spark.kubernetes.driver.pod.name=spark-driver `
    --conf spark.kubernetes.executor.instances=1 `
    --conf spark.pyspark.python=/usr/bin/python3 `
    --conf spark.pyspark.driver.python=/usr/bin/python3 `
    --py-files local:///opt/<your-egg-file>.egg `
    local:///opt/src/main/python/<your-script>.py
  ```

  </details>

```bash
kubectl logs spark-driver
```

## 7. Destroy Infrastructure (Required Step)

After completing all steps, **destroy the infrastructure** to clean up all deployed resources.

⚠️ **Warning:** This action is **irreversible**. Running the command below will **delete all infrastructure components** created in previous steps.

1. Identify entities attached to the policy:

```bash
aws iam list-entities-for-policy --policy-arn arn:aws:iam::<aws-account-id>:policy/S3SparkAccessPolicy
```

2. Detach the policy from the entity listed in the previous step.

```bash
aws iam detach-role-policy --role-name <RoleName> --policy-arn arn:aws:iam::<aws-account-id>:policy/S3SparkAccessPolicy
```

3. Delete ecr repository

```bash
aws ecr delete-repository --repository-name spark-python-06
```

4. Remove all deployed resources, run:

```bash
terraform destroy
```