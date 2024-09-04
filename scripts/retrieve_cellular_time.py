#!/usr/bin/env python3
#-*- coding: utf-8 -*-

from utils.shared_functions import get_cellular_time

def main():
	try:
		current_datetime = get_cellular_time()
		print(current_datetime)
	
	except Exception as e:
		print(f"Error: {e}", file=sys.stderr)
		exit(1)

if __name__ == "__main__":
	main()
