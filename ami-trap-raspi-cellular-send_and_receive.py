from amitrap_cellular import cellular_send_and_receive
import asyncio


if __name__ == "__main__":

    try:

        asyncio.run(cellular_send_and_receive())

    except Exception as e:
        print()
        print(f"An error occurred: {e}")
        print()
        print("Terminating cellular_send...")
        print()
        pass
