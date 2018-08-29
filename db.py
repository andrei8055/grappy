import sqlite3

#python script to dump DB content to console

#Create DB
conn = sqlite3.connect('output/goodreads.sqlite')
print "Opened database successfully";


#Print profiles
cursor = conn.execute("SELECT * from PROFILE")
for row in cursor:
   print "URL = ", row[0]
   print "NAME = ", row[1]
   print "PICTURE = ", row[2]
   print "DETAILS = ", row[3]
   print "DOB = ", row[4]
   print "WEBSITE = ", row[5]
   print "ACTIVITY = ", row[6]
   print "INTERESTS = ", row[7]
   print "FAVOURITES = ", row[8]
   print "ABOUT = ", row[9]
   print "-----------------"

print "Operation done successfully";


conn.close()
