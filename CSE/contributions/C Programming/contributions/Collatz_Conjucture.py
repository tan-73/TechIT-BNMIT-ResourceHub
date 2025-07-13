def collatz(num):
    steps = 0
    L = []
    while num != 1:
        print(num)
        if num % 2 == 0:
            num = int(num / 2)
            steps += 1
            L.append(num)
        else:
            num = int((3 * num) + 1)
            steps += 1  
            L.append(num)
    else:
        print(num)
        print('Number of steps =',steps)
        if L != []:
            print('Highest number =', max(L))
        
            
def main():
    num = int(input('\nInput 0 to exit or enter an integer: '))
    if num != 0:
        collatz(num)
    else:
        exit()

while True:
    main()
