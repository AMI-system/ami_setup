#!/usr/bin/env python3
#-*- coding: utf-8 -*-

from utils.shared_functions import get_cellular_time
from datetime import datetime

def main():
	try:
		current_datetime = get_cellular_time()
		print(current_datetime.strftime('%Y-%m-%d %H:%M:%S'))
	
	except Exception as e:
		print(f"Error: {e}")
		exit(1)

if __name__ == "__main__":
	main()
