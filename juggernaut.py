import math
from datetime import date, timedelta

dummy_current_one_rep_max = {
    'bench':...,
    'squat':...,
    'deatlft':...,
    'press':...,
}

class Program:

    def _init_(self,current_one_rep_max=dummy_current_one_rep_max):
        self.current_one_rep_max = current_one_rep_max

    def get_set(self,pcntg,rep,sets,item):
        return {'item':item,
                'reps':rep,
                'sets':sets,
                'weight':math.ceil(self.current_one_rep_max[item]*pcntg)}


    # -------------------
    # 10s WAVE
    # -------------------

    def tens_accumulation(self, item):
        return self.get_set(0.60, 5, 10, item)

    def tens_intensification(self, item):
        return [
            self.get_set(0.55, 5, 1, item),
            self.get_set(0.625, 5, 1, item),
            self.get_set(0.675, 3, 10, item),
        ]

    def tens_realization(self, item):
        return [
            self.get_set(0.50, 5, 1, item),
            self.get_set(0.60, 3, 1, item),
            self.get_set(0.70, 1, 1, item),
            self.get_set(0.75, 'AMAP', 1, item),
        ]

    # -------------------
    # 8s WAVE
    # -------------------

    def eights_accumulation(self, item):
        return self.get_set(0.65, 5, 8, item)

    def eights_intensification(self, item):
        return [
            self.get_set(0.60, 3, 1, item),
            self.get_set(0.675, 3, 1, item),
            self.get_set(0.725, 3, 8, item),
        ]

    def eights_realization(self, item):
        return [
            self.get_set(0.50, 5, 1, item),
            self.get_set(0.60, 3, 1, item),
            self.get_set(0.70, 2, 1, item),
            self.get_set(0.75, 1, 1, item),
            self.get_set(0.80, 'AMAP', 1, item),
        ]

    # -------------------
    # 5s WAVE
    # -------------------

    def fives_accumulation(self, item):
        return self.get_set(0.70, 6, 5, item)

    def fives_intensification(self, item):
        return [
            self.get_set(0.65, 2, 1, item),
            self.get_set(0.725, 2, 1, item),
            self.get_set(0.775, 4, 5, item),
        ]

    def fives_realization(self, item):
        return [
            self.get_set(0.50, 5, 1, item),
            self.get_set(0.60, 3, 1, item),
            self.get_set(0.70, 2, 1, item),
            self.get_set(0.75, 1, 1, item),
            self.get_set(0.80, 1, 1, item),
            self.get_set(0.85, 'AMAP', 1, item),
        ]

    # -------------------
    # 3s WAVE
    # -------------------

    def threes_accumulation(self, item):
        return self.get_set(0.75, 7, 3, item)

    def threes_intensification(self, item):
        return [
            self.get_set(0.70, 1, 1, item),
            self.get_set(0.775, 1, 1, item),
            self.get_set(0.82, 5, 3, item),
        ]

    def threes_realization(self, item):
        return [
            self.get_set(0.50, 5, 1, item),
            self.get_set(0.60, 3, 1, item),
            self.get_set(0.70, 2, 1, item),
            self.get_set(0.75, 1, 1, item),
            self.get_set(0.80, 1, 1, item),
            self.get_set(0.85, 1, 1, item),
            self.get_set(0.90, 'AMAP', 1, item),
        ]

    def get_weeks(self,n_weeeks = 3):
        
        today = date.today()
        this_monday = today - timedelta(days=today.weekday())

        mondays = [
            (this_monday - timedelta(weeks=i)).strftime("%Y-%m-%d")
            for i in range(n_weeeks)
        ]

        print(mondays)

if __name__ == 'main':
    self = program = Program()
    weeks = program.get_weeks()