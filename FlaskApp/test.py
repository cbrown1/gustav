import time

max = 100
sleep = 2
running = True
elapsed = 0
with open("test_start.txt", "w") as f:
    f.write("test started")
while running:
    print(f"Running for {elapsed} s")
    time.sleep(sleep)
    elapsed += sleep
    if elapsed > max:
        running = False
with open("test_start.txt", "a+") as f:
    f.write("test finished")
print(f"FIN")
