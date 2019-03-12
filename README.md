# EC2 Automation Script
Python script to automate the creation of ec2, installing an apache web server, monitor the instance.
After the instance is created, the script makes sure that the instance is running. (We need to make sure for the SSH to work)
The script checks if the apache web server is running on the instance by uploading the check_webserver.py script using SCP and if
it's not running, it will start the apache web server. When this is complete, the script creates an S3 bucket and puts an image
into it. The script overwrites the index.html file with the html code and includes path to the image in the S3 bucket. The script provides a link
that you can use to check the image on the ec2 instance. You can also check the Access and Error logs of the apache webserver on the ec2 instance.
