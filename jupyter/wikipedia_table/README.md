
## Scrape Wikipedia table

### Pandas not allowed.


    sudo apt-get install python3-mysqldb
    sudo apt-get install mysql-client
  
    sudo apt-get install libmariadb-dev libmariadbclient-dev libmysqlclient-dev
    

### Python set up
Commands below for different Python environments. I personally use `pipenv` and `pip`.

Haven't used conda, so no guarantees :stuck_out_tongue:
 
    
##### Pipenv

    pipenv install
    
##### Pip

    pip install -r requirements.txt
    
##### Anaconda
    conda install --yes --file requirements.txt    
    
### Set up user & db 

The database schema is in a file called `create_db.sql`

    mysql -h <host>> -u <super user>> -p  < "create_db.sql"
    
    mysql -h 172.33.0.100 -u root -p  < "create_db.sql"
    
    
    
### Clean up

    isort ./*.py
    black -l 79 -t py36 ./*.py
    
    jupyter nbextension install https://github.com/drillan/jupyter-black/archive/master.zip --user
    jupyter nbextension enable jupyter-black-master/jupyter-black
    
### Docs

    make html
    sphinx-build -b rinoh source _build/rinoh