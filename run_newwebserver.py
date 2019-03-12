#!/usr/bin/env python3
import boto3
import time
import subprocess
import datetime
ec2 = boto3.resource('ec2')
client = boto3.client('ec2')
s3 = boto3.resource("s3")
# setting an empty string to the bucket name variable
bucket_name = ''
# defining the image path
object_name = 'index.jpeg'


# this method uses scp to copy the local script to the ec2 instance
def copyFile():
    try:
      # using SCP to copy the local script to my ec2 instance
      scp = 'scp -o StrictHostKeyChecking=no -i InstanceKey.pem check_webserver.py ec2-user@'+instance[0].public_ip_address+':.'
      subprocess.run(scp, check=True, shell=True)
      return True
    except subprocess.CalledProcessError:
      return False

# this method uses the ssh command to install python 3.6 on my ec2 instance, set the permissions of the check_webserver.py script to 700 and execute the script on the ec2 instance
def checkWebServer():
    try:
      # using the ssh to install python 3.6 on the ec2 instance, hiding the output from the console (stdout=subprocess.DEVNULL)
      ssh = "ssh -i InstanceKey.pem ec2-user@" + instance[0].public_ip_address + " 'sudo yum -y install python36'"
      subprocess.run(ssh, check=True, shell=True, stdout=subprocess.DEVNULL)
      # using the ssh to set check_webserver.py permissions
      ssh1 = "ssh -i InstanceKey.pem ec2-user@" + instance[0].public_ip_address + " 'chmod 700 check_webserver.py'"
      subprocess.run(ssh1, check=True, shell=True)
      # using the ssh to execute the check_webserver.py script with python
      ssh2 = "ssh -i InstanceKey.pem ec2-user@" + instance[0].public_ip_address + " 'python36 check_webserver.py'"
      subprocess.run(ssh2, check=True, shell=True)
      return True
    except subprocess.CalledProcessError:
      return False

# this method is creating an s3 bucket using the user input value and making sure the bucket name will be unique, also setting public read permissions
def createBucket():
    try:
        # using the global variable
        global bucket_name
        # getting user
        bucket = input("Enter the bucket name: ")
        # getting a unique value (using current time)
        time = '-'+str(datetime.datetime.now().time())
        # replacing the : with a - since : is not allowed in a bucket name
        timenew = time.replace(":","-")
        # joining the strings together and assigning it to a global variable
        bucket_name = bucket + timenew
        # creating an s3 bucket
        s3.create_bucket(Bucket=bucket_name, CreateBucketConfiguration={'LocationConstraint': 'eu-west-1'}, ACL='public-read')
        return True
    except Exception as error:
      return False

# this method uses the global variable bucket_name with the object_name to put the image into the bucket, also setting public read permissions
def putBucket():
    try:
        # using the global variable bucket_name with the object_name to put the image into the bucket
        s3.Object(bucket_name, object_name).put(Body=open(object_name, 'rb'), ACL='public-read')
        return True
    except Exception as error:
        return False

# this method is writing html code into a local index.html file and then using scp to upload it to my ec2 instance, then setting var/www/html permissions to 777 and copying the index file into it
def configureWebPage():
    try:
        #path to my index file
        html = 'index.html'
        #opening the index file as 'w' (It will overwrite the contents)
        with open(html, 'w') as filetowrite:
            # adding html code to the file with our variables (bucket_name and object_name)
            filetowrite.write('<html><h1><i>Your uploaded <a href="https://s3-eu-west-1.amazonaws.com/'+bucket_name+'/'+object_name+'">image</a> is shown below</i></h1><img src="https://s3-eu-west-1.amazonaws.com/'+bucket_name+'/'+object_name+'"></html>')
            filetowrite.close()
        # using scp to copy the index file to the ec2 instance
        scp = 'scp -o StrictHostKeyChecking=no -i InstanceKey.pem index.html ec2-user@' + instance[0].public_ip_address + ':.'
        subprocess.run(scp, check=True, shell=True)
        # setting the var/www/html folder permissions and copying the index file into it
        ssh1 = "ssh -i InstanceKey.pem ec2-user@" + instance[0].public_ip_address + " 'sudo chmod 777 /var/www/html; sudo cp index.html /var/www/html'"
        subprocess.run(ssh1, check=True, shell=True)
        return True
    except Exception as error:
        return False




# this method is used to print apache logs and handle the input accordingly
def apacheLogs():
    #printing menu
    print("---Apache Logs---")
    print("1. Access Logs")
    print("2. Error Logs")
    print("3. Exit")
    # getting the choice input
    logInput = int(input("Enter your choice:"))
    # error checking & handling
    while (logInput > 3 | logInput < 1):
        logInput = int(input("Invalid input, try again:"))
    # looping the menu until the user picks 3 (Exit)
    while (logInput != 3):
        # when user picks Access Logs
        if (logInput == 1):
            # ssh to the ec2 and set permissions of the /var/log/httpd to 777, after that read the contents of access_log file
            ssh = "ssh -i InstanceKey.pem ec2-user@" + instance[0].public_ip_address + " 'sudo chmod 777 /var/log/httpd; sudo cat /var/log/httpd/access_log'"
            subprocess.run(ssh, check=True, shell=True)
        # when user picks Error Logs
        elif(logInput == 2):
            # ssh to the ec2 and set permissions of the /var/log/httpd to 777, after that read the contents of error_log file
            ssh = "ssh -i InstanceKey.pem ec2-user@" + instance[0].public_ip_address + " 'sudo chmod 777 /var/log/httpd; sudo cat /var/log/httpd/error_log'"
            subprocess.run(ssh, check=True, shell=True)
        print("---Apache Logs---")
        print("1. Access Logs")
        print("2. Error Logs")
        print("3. Exit")
        logInput = int(input("Enter your choice:"))
        while (logInput > 3 | logInput < 1):
            logInput = int(input("Invalid input, try again:"))
    # when the user escapes the loop (picks number 3)
    print("Task finished, you have exited the program.")

#test method to compare each method
def test(got, expected):
  if got == expected:
    prefix = ' OK '
  else:
    prefix = '  X '
  print('%s got: %s expected: %s' % (prefix, repr(got), repr(expected)))

#creating the ec2 instance with predefined Security Group, Tags, UserData etc. It will update the ec2 instance and install apache.
print ("Creating an ec2 Instance...")
instance = ec2.create_instances(
    ImageId='ami-047bb4163c506cd98',
    MinCount=1,
    MaxCount=1,
    KeyName='InstanceKey',
    InstanceType='t2.micro',
      SecurityGroups=[
        'SecurityGroup',
    ],
    TagSpecifications=[
        {
            'ResourceType':'instance',
            'Tags': [
                {
                    'Key':'Name',
                    'Value':'Assignment'
                 },
             ]

         }],
    UserData="""#!/bin/bash
sudo yum update -y
sudo yum install httpd -y
sudo systemctl enable httpd"""
)

print ("Instance with the id "+instance[0].id+" has been created")
print ("Waiting for the instance to start...")

#looping until the instance is running (Using reload to refresh data)
while instance[0].state['Name'] != "running":
    time.sleep(0.1)
    instance[0].reload()

#setting another sleep after the instance has started for it to allow ssh
time.sleep(50)
print(instance[0].id+" is running, uploading script...")

#running and checking the status of the scp upload
if copyFile():
    print("script uploaded successfully, making sure the webserver is running...")
    time.sleep(10)
    # running the check_webserver.py script and getting the status
    if checkWebServer():
        print("web server is now running... creating an S3 bucket...")
        # creating the bucket and getting the status (Fail or Pass)
        if createBucket():
            print("bucket created... uploading the image to the bucket...")
            # uploading the image to the bucket and getting the status (Fail or Pass)
            if putBucket():
                print("Image uploaded successfully.. configuring web server...")
                # writing the html code into the index.html file, using scp to copy it to my ec2 instance and copying the file using cp command to the var/www/html. Also getting the status of the operation.
                if configureWebPage():
                    print("Image can now be displayed using this link - http://"+instance[0].public_ip_address)
                  # displaying apache log menu
                    apacheLogs()

                # if configureWebPage() has an Exception
                else:
                    print("Error configuring web server..")
            # if putBucket() has an Exception
            else:
                print("Error uploading image..")
        # if createBucket() has an Exception
        else:
            print("Error creating a bucket...")
    # if checkWebServer() has an Exception
    else:
        print("Error checking web server, possibly script is missing!")
# if copyFile() has an Exception
else:
    print("script uploading failed... please make sure the script is in your working directory")


