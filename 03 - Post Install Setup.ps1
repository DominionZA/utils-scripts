# netsh interface portproxy add v4tov4 listenaddress=127.0.0.1 listenport=3306 connectaddress=192.168.1.10 connectport=3306

powercfg -duplicatescheme e9a42b02-d5df-448d-aa00-03f14749eb61

# Set the keyboard repeat rate to the maximum value
Set-ItemProperty -Path "HKCU:\Control Panel\Keyboard" -Name "KeyboardSpeed" -Value 31

git clone https://michael_smit@bitbucket.org/cosoft-ondemand/aura_portal.git "C:\Source\Aura Portal"
git clone https://michael_smit@bitbucket.org/cosoft-ondemand/cloud_backend.git "C:\Source\Cloud Backend"
git clone https://michael_smit@bitbucket.org/cosoft-ondemand/cloud_reports.git "C:\Source\Cloud Reports"


git config --global user.email "msmit@cosoft.co.za"
git config --global user.name "Michael Smit"
git config --global core.worktree "C:\Source"

# Pull the MySQL image
docker pull mysql:8

# Run the MySQL container
docker run -d --name Test `
  -e MYSQL_ROOT_PASSWORD="P@ssw0rd1" `
  -e MYSQL_USER="aura" `
  -e MYSQL_PASSWORD="P@ssw0rd1" `
  -e MYSQL_DATABASE="TestDB" `
  --restart always `
  -p 3306:3306 `
  mysql:8

Start-Sleep -Seconds 30

docker exec -i Test mysql -u root -pP@ssw0rd1 -e "CREATE USER 'admin'@'%' IDENTIFIED BY 'P@ssw0rd1'; GRANT ALL PRIVILEGES ON *.* TO 'admin'@'%' WITH GRANT OPTION; FLUSH PRIVILEGES;"
docker exec -i Test mysql -u root -pP@ssw0rd1 -e "CREATE USER 'frank'@'%' IDENTIFIED BY 'P@ssw0rd1'; GRANT ALL PRIVILEGES ON *.* TO 'frank'@'%' WITH GRANT OPTION; FLUSH PRIVILEGES;"

# Pull the Redis image
docker pull redis:latest

# Run the Redis container
docker run -d --name redis `
  --restart always `
  -p 6379:6379 `
  redis:latest