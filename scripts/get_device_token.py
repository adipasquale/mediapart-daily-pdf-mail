from rmapy.api import Client
import sys

rmapy = Client()
rmapy.register_device(sys.argv[0])
print("your device token is:")
print("---")
print()
print(rmapy.token_set["devicetoken"])
print()
print("---")
