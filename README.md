# DevOpsBot_PT_START

### Telegram bot using Python + PostgreSQL

## Features:
* Find email addresses and phone numbers in text
* Connect remotely to Linux machine using SSH and retrieves information about system operation
* It is possible to save the found data to the Database
* Db replication

## Run
### Docker
To run with docker:</br>
`docker-compose build` and then `docker-compose up`

### Ansible
To run with ansible:</br>
Specify hosts in `inventory` and `vars.yml` - you need 2 Linux machines for running and 1 for executing playbook.</br>
Run: `ansible-playbook -i inventory playbook_tg_bot.yml`

