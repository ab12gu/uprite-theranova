def move():
    print("Test.")


func_dict = {'move': move}
if __name__ == "__main__":
    input("Press enter to begin.")
    currentEnvironment = "room"  # getNewEnvironment(environments)
    currentTimeOfDay = "1 A.M."  # getTime(timeTicks, timeOfDay)
    print("You are standing in the {0}. It is {1}.".format(currentEnvironment,
                                                           currentTimeOfDay))
    command = input("> ")
    func_dict[command]()
