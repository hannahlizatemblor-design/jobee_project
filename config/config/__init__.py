import pymysql
import sys

# We "fake" the version info so Django stops complaining
pymysql.version_info = (8, 0, 11, 'final', 0)
pymysql.install_as_MySQLdb()

# This is the "magic" line if the error still persists
# It tells Django that the MySQL client is already loaded
sys.modules['MySQLdb'] = pymysql
