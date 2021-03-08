import time

duration = 100
sleep = 2
running = True
elapsed = 0
with open("test_start.txt", "w") as f:
    f.write("test started")
while running:
    print(f"Running for {elapsed} s")
    time.sleep(sleep)
    elapsed += sleep
    if elapsed >= duration:
        running = False
with open("test_start.txt", "a+") as f:
    f.write("test finished")
print(f"FIN")

# Check if process is alive
poll = proc.poll()
if poll is None:
    print('Alive')
else:
    print('Dead')
