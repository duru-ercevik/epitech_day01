first_list=[1,1,1,1,2,2,2,2,2] 
second_list=[42, '42', 42.0, 21 + 21, 42 * 10 / 10]

def delete_duplicates(lst):
    result_list=[]
    for i in lst:
        if i not in result_list:
            result_list.append(i)
    return result_list

print(delete_duplicates(first_list))
print(delete_duplicates(second_list))