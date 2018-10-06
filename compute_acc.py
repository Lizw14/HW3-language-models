#!/usr/bin/env python

import os


list1 = os.listdir('out1_')
list2 = os.listdir('out2_')



list1.sort(key=float)
list2.sort(key=float)

min_entropy = 9999
max_acc = 0
max_count = 0
min_c_en = ""

max_c_acc =""

for i in range(len(list1)):

    print(str(list1[i]))
    with open('out1_/'+list1[i],"r") as reader:
        line = reader.read()
        split_line = line.split()
        try:
            sum_acc1 = float(split_line[0])

            entropy1 = float(split_line[1])
            #print(entropy1)
            
            file_num1 = float(split_line[2])

            token_num1 = float(split_line[3])
            count_num1 = float(split_line[4])
            #print(token_num1)
        except:
            print(split_line)
            print(list1[i])


    with open('out2_/'+list2[i],"r") as reader:
        line = reader.read()
        split_line = line.split()
        try:

            sum_acc2 = float(split_line[0])
            entropy2 = float(split_line[1])
            #print(entropy2)
            file_num2 = float(split_line[2])
            token_num2 = float(split_line[3])
            count_num2 = float(split_line[4])
            #print(token_num2)
        except:
            print(split_line)
            print(list2[i])

    
    acc_sum = sum_acc1+sum_acc2

    file_sum = file_num1+file_num2

    average_acc = acc_sum/file_sum

    entrop_sum = entropy1+entropy2

    token_sum = token_num1+token_num2

    average_entrop = entrop_sum/token_sum
    
    count_sum = count_num1+count_num2
    count_acc = count_sum/file_sum
    count_acc1 = count_num1/file_num1
    count_acc2 = count_num2/file_num2

    print(acc_sum, sum_acc1, sum_acc2, average_acc)
    print(entrop_sum, entropy1, entropy2, average_entrop)
    print(count_acc, count_acc1, count_acc2)

    if average_acc > max_acc:
        max_acc = average_acc
        max_c_acc = list1[i]

    if average_entrop < min_entropy:
        min_entropy = average_entrop
        min_c_en = list1[i]

    if count_acc > max_count:
        max_count = count_acc
        max_c_count = list1[i]

print("MAXIMUM!")
print(max_acc)
print(max_c_acc+ "\n")

print("MINIMUM!")
print(str(min_entropy))
print(min_c_en)

print("MAXIMUM!")
print(max_count)
print(max_c_count)
