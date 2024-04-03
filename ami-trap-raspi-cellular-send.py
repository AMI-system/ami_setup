from amitrap_cellular import cellular_send
import asyncio


if __name__ == "__main__":

    try:

        asyncio.run(cellular_send())

    except Exception as e:
        print()
        print(f"An error occurred: {e}")
        print()
        print("Terminating cellular_send...")
        print()
        pass
