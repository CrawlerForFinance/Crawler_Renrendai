from distutils.core import setup  
import py2exe  
import sys
includes = ["encodings", "encodings.*"]    
sys.argv.append("py2exe")  
options = {"py2exe":   { "bundle_files": 0 }  }
setup(console=['SPCrawler_renrendai.py','UPCrawler_renrendai.py','OrderCrawler_renrendai.py','Crawler_renrendai.py'])
#setup(console=['SPCrawler_renrendai.py'])