from sql_lookup import get_user


print("Normal lookup:", get_user("1"))

print("Attack input: ", get_user("1 OR 1=1"))