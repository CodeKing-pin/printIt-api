import sqlite3
con=sqlite3.connect('printJobs.db')
cur=con.cursor()
cur.execute("CREATE table printjobs(time,numPages,printerName,success)")