day = input("Enter the day: ")

match day:
    case "saturday" | "sunday":
        print(f"{day} is a weekend")
    case "monday" | "tuesday" | "wednesday" | "thursday" | "friday":
        print(f"{day} is a weekday")
    case _:
        print("That is not a valid day")