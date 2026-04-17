#lex_auth_012693750719488000124

def get_count(num_list):
    count=0

    for i in range(len(num_list)-1):
        if(num_list[i]==num_list[i+1]):
            count+=1
    return count
#provide different values in list and test your program
num_list=[1,1,5,100,-20,-20,6,0,0]
print(get_count(num_list))
num_list2=[98, 97, 97, 98]
print(get_count(num_list2))