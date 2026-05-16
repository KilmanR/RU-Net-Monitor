class Morning:
    def wake_up():
        for hour in day:
            if energy == "low":
                mug.pour("coffee")
                mind.start()
            elif energy == "full":
                mug.close()
                task.run()

class Evening:
    def wind_down():
        for hour in night:
            if stress == "high":
                cup.brew("tea")
                system.calm()
            elif stress == "low":
                cup.put_back()
                sleep.init()