import calendar

y = int(input("Enter the year: "))
m = 4

print("Your calendar")

cal = calendar.TextCalendar(calendar.SUNDAY)

i = 1
while i <= 1:
    cal.prmonth(y,m, i)
    i += 1
