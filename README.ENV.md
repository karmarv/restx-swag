
### Installation Guide 

#### OS Packages
- AWS EC2 instance as the deployment environment
  ```bash
  #ssh -i ec-rsa.pem ec2-user@ec2-3-16-163-228.us-east-2.compute.amazonaws.com
  ssh -i ec-rsa.pem  ubuntu@ec2-52-14-9-128.us-east-2.compute.amazonaws.com
  ```
- Install basic packages for administration
  ```bash
  #sudo yum install -y docker vim tmux git mesa-libGL postgresql
  sudo apt-get install -y vim tmux git postgresql libsm6 libxext6 ffmpeg libfontconfig1 libxrender1 libgl1-mesa-glx
  ```
- Installation via Miniconda v24.3.0 - https://docs.conda.io/projects/miniconda/en/latest/
  ```bash
  mkdir -p ~/miniconda3
  wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda3/miniconda.sh
  bash ~/miniconda3/miniconda.sh -b -u -p ~/miniconda3
  rm -rf ~/miniconda3/miniconda.sh
  ```
  ```bash
  ~/miniconda3/bin/conda init bash
  ~/miniconda3/bin/conda init zsh
  ```
  - create virtual environment
  ```bash
  conda env remove -n restx
  conda create -n restx python=3.10
  conda activate restx
  ```


#### Docker services
- Install docker on AWS Linux Ec2 instance for Redis and Postgresql services
  ```bash
  sudo apt install apt-transport-https ca-certificates curl software-properties-common
  curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
  echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
  sudo apt update
  apt-cache policy docker-ce
  sudo apt install docker-ce
  sudo systemctl status docker
  sudo usermod -aG docker ${USER}
  ```
  - Install docker-compose
  ```bash
  sudo apt-get install docker-compose-plugin
  docker compose version
  ```
  - Start :`docker compose up -d --build`
  - Logs  :`docker compose logs`
  - Stop  :`docker compose down -v`
- Access the services by their container name
  - Postgres: `sudo docker exec -it restx-swag-postgres_db-1 psql -U restx -d restxdb`
  - Redis: `sudo docker exec -it restx-swag-redis_db-1 redis-cli`
