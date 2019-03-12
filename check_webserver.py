#!/usr/bin/python3

"""A tiny Python program to check that httpd is running.
Try running this program from the command line like this:
  python3 check_webserver.py
"""

import subprocess
#checking the httpd service
def checkhttpd():
  try:
    #checking httpd processes
    cmd = 'ps -A | grep httpd'
    
    subprocess.run(cmd, check=True, shell=True)
    print("Web Server IS already running")
   #if it is not running
  except subprocess.CalledProcessError:
    print("Web Server is not running, starting service...")
	#starting the httpd service
    start = 'sudo service httpd start'
    subprocess.run(start, check=True, shell=True)
    
    
# Define a main() function.
def main():
    checkhttpd()
      
# This is the standard boilerplate that calls the main() function.
if __name__ == '__main__':
  main()