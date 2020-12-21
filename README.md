## Set Up

* Install [Docker](https://docs.docker.com/engine/install/)
* Install docker-compose

Debian set up for docker is [here](https://docs.docker.com/engine/install/debian/)
Make sure you do the [post-install steps](https://docs.docker.com/engine/install/linux-postinstall/)

Install docker

    sudo apt-get remove docker docker-engine docker.io containerd runc
    sudo apt-get update
    
    sudo apt-get install \
        apt-transport-https \
        ca-certificates \
        curl \
        gnupg-agent \
        software-properties-common
        
    curl -fsSL https://download.docker.com/linux/debian/gpg | sudo apt-key add -
    sudo apt-key fingerprint 0EBFCD88
    
    sudo add-apt-repository \
       "deb [arch=amd64] https://download.docker.com/linux/debian \
       $(lsb_release -cs) \
       stable"
       
    sudo apt-get update
    sudo apt-get install docker-ce docker-ce-cli containerd.io
    sudo groupadd docker
    sudo usermod -aG docker $USER
       
       
       
Install docker-compose

    sudo pip install docker-compose
    

    
### Run Docker spark cluster
Run

    docker-compose up

Any issues building, then try 

    docker-compose up --build  --force-recreate  
       
Spark url is [http://localhost:8081/](http://localhost:8081/)

Zeppelin url is [http://localhost:9080/](http://localhost:9080/#/)
Livy [http://localhost:8998/ui](http://localhost:8998/ui)


### Setting up black

    pip install black
    jupyter nbextension install https://github.com/drillan/jupyter-black/archive/master.zip 
    jupyter nbextension