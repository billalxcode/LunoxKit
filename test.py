import sys 
print("FAILED..............") 
sys.stdout.write("\033[F") #back to previous line 
sys.stdout.write("\033[K") #clear line 
print("SUCCESS!") 