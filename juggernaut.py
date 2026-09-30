import math
from datetime import date, timedelta
from pathlib import Path

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Font
from openpyxl.utils import get_column_letter


# ============================================================
# CONFIG
# ============================================================

LIFTS = [
    "bench",
    "squat",
    "deadlift",
    "press",
]


DEFAULT_ONE_REP_MAX = {
    "bench": 100,
    "squat": 140,
    "deadlift": 180,
    "press": 60,
}


# Internally the deloads need unique names.
# Otherwise Python cannot tell which "deload" comes next.
PHASE_ORDER = [
    "tens_accumulation",
    "tens_intensification",
    "tens_realization",
    "tens_deload",

    "eights_accumulation",
    "eights_intensification",
    "eights_realization",
    "eights_deload",

    "fives_accumulation",
    "fives_intensification",
    "fives_realization",
    "fives_deload",

    "threes_accumulation",
    "threes_intensification",
    "threes_realization",
    "threes_deload",
]


# What is shown to the user.
def display_phase(phase):
    if phase.endswith("_deload"):
        return "deload"
    return phase


DEFAULT_STARTING_WEEK = {
    "week": "2026-09-28",

    "bench": "fives_realization",
    "squat": "threes_intensification",

    # Specify WHICH deload because this determines
    # which phase comes next.
    "deadlift": "threes_deload",

    "press": "tens_accumulation",
}


# ============================================================
# WORKOUT DEFINITIONS
# ============================================================
#
# Each tuple is:
#
#   (percentage_of_1rm, reps, sets)
#
# Having the workouts as data instead of many almost-identical
# functions makes the program much easier to maintain.
# ============================================================

WORKOUTS = {

    # --------------------
    # 10s
    # --------------------

    "tens_accumulation": [
        (0.60, 5, 10),
    ],

    "tens_intensification": [
        (0.55, 5, 1),
        (0.625, 5, 1),
        (0.675, 3, 10),
    ],

    "tens_realization": [
        (0.50, 5, 1),
        (0.60, 3, 1),
        (0.70, 1, 1),
        (0.75, "AMAP", 1),
    ],

    # --------------------
    # 8s
    # --------------------

    "eights_accumulation": [
        (0.65, 5, 8),
    ],

    "eights_intensification": [
        (0.60, 3, 1),
        (0.675, 3, 1),
        (0.725, 3, 8),
    ],

    "eights_realization": [
        (0.50, 5, 1),
        (0.60, 3, 1),
        (0.70, 2, 1),
        (0.75, 1, 1),
        (0.80, "AMAP", 1),
    ],

    # --------------------
    # 5s
    # --------------------

    "fives_accumulation": [
        (0.70, 6, 5),
    ],

    "fives_intensification": [
        (0.65, 2, 1),
        (0.725, 2, 1),
        (0.775, 4, 5),
    ],

    "fives_realization": [
        (0.50, 5, 1),
        (0.60, 3, 1),
        (0.70, 2, 1),
        (0.75, 1, 1),
        (0.80, 1, 1),
        (0.85, "AMAP", 1),
    ],

    # --------------------
    # 3s
    # --------------------

    "threes_accumulation": [
        (0.75, 7, 3),
    ],

    "threes_intensification": [
        (0.70, 1, 1),
        (0.775, 1, 1),
        (0.82, 5, 3),
    ],

    "threes_realization": [
        (0.50, 5, 1),
        (0.60, 3, 1),
        (0.70, 2, 1),
        (0.75, 1, 1),
        (0.80, 1, 1),
        (0.85, 1, 1),
        (0.90, "AMAP", 1),
    ],
}


# Change this to your preferred deload prescription.
DELOAD = [
    (0.50, 5, 5),
]


# ============================================================
# PROGRAM
# ============================================================

class Program:

    def __init__(
        self,
        current_one_rep_max=None,
        starting_week=None,
    ):

        if current_one_rep_max is None:
            current_one_rep_max = DEFAULT_ONE_REP_MAX

        if starting_week is None:
            starting_week = DEFAULT_STARTING_WEEK

        self.current_one_rep_max = current_one_rep_max.copy()
        self.starting_week = starting_week.copy()

        self.validate()

    # ========================================================
    # VALIDATION
    # ========================================================

    def validate(self):

        for lift in LIFTS:

            if lift not in self.current_one_rep_max:
                raise ValueError(f"Missing 1RM for {lift}")

            phase = self.starting_week[lift]

            if phase not in PHASE_ORDER:
                raise ValueError(
                    f"Invalid starting phase for {lift}: {phase}"
                )

    # ========================================================
    # DATE HELPERS
    # ========================================================

    @staticmethod
    def this_monday():

        today = date.today()

        return today - timedelta(
            days=today.weekday()
        )

    @staticmethod
    def to_monday(value):

        if isinstance(value, str):
            value = date.fromisoformat(value)

        return value - timedelta(
            days=value.weekday()
        )

    # ========================================================
    # SCHEDULE
    # ========================================================

    def get_phase(self, lift, week=None):
        """
        Return the phase for a lift on a particular week.
        """

        if week is None:
            week = self.this_monday()

        week = self.to_monday(week)

        anchor_week = date.fromisoformat(
            self.starting_week["week"]
        )

        anchor_week = self.to_monday(anchor_week)

        weeks_from_start = (
            week - anchor_week
        ).days // 7

        start_phase = self.starting_week[lift]

        start_index = PHASE_ORDER.index(start_phase)

        phase_index = (
            start_index + weeks_from_start
        ) % len(PHASE_ORDER)

        return PHASE_ORDER[phase_index]

    # ========================================================
    # WORKOUT
    # ========================================================

    def get_workout_template(self, phase):

        if phase.endswith("_deload"):
            return DELOAD

        return WORKOUTS[phase]

    def get_workout(self, lift, week=None):

        phase = self.get_phase(lift, week)

        workout = []

        for percentage, reps, sets in self.get_workout_template(phase):

            weight = math.ceil(
                self.current_one_rep_max[lift]
                * percentage
            )

            workout.append({
                "percentage": percentage,
                "weight": weight,
                "reps": reps,
                "sets": sets,
            })

        return {
            "lift": lift,
            "phase": phase,
            "sets": workout,
        }

    # ========================================================
    # CHANGE 1RM
    # ========================================================

    def set_one_rep_max(self, lift, value):

        if lift not in LIFTS:
            raise ValueError(
                f"Unknown lift: {lift}"
            )

        self.current_one_rep_max[lift] = value

    def set_one_rep_maxes(self, **values):

        for lift, value in values.items():
            self.set_one_rep_max(
                lift,
                value,
            )

    # ========================================================
    # PRINT CURRENT WEEK
    # ========================================================

    def print_this_week(self):

        week = self.this_monday()

        print()
        print("=" * 65)
        print(f"WEEK OF {week}")
        print("=" * 65)

        for lift in LIFTS:

            workout = self.get_workout(
                lift,
                week,
            )

            print()
            print(
                f"{lift.upper()} "
                f"[{display_phase(workout['phase'])}]"
            )

            print("-" * 45)

            for s in workout["sets"]:

                print(
                    f"{s['sets']} x {s['reps']} "
                    f"@ {s['weight']} "
                    f"({s['percentage'] * 100:g}%)"
                )

        print()

    # ========================================================
    # PRINT N-WEEK OVERVIEW
    # ========================================================

    def print_overview(self, n_weeks=10):

        week = self.this_monday()

        print()
        print("PROGRAM OVERVIEW")
        print("=" * 100)

        print(
            f"{'Week':<12}"
            f"{'Bench':<24}"
            f"{'Squat':<24}"
            f"{'Deadlift':<24}"
            f"{'Press':<24}"
        )

        print("-" * 100)

        for i in range(n_weeks):

            current_week = (
                week
                + timedelta(weeks=i)
            )

            phases = [
                display_phase(
                    self.get_phase(
                        lift,
                        current_week,
                    )
                )
                for lift in LIFTS
            ]

            print(
                f"{str(current_week):<12}"
                f"{phases[0]:<24}"
                f"{phases[1]:<24}"
                f"{phases[2]:<24}"
                f"{phases[3]:<24}"
            )

        print()

    # ========================================================
    # EXCEL FORMULA
    # ========================================================

    def workout_excel_formula(
        self,
        phase,
        one_rep_max_cell,
    ):
        """
        Build an Excel formula containing:

        phase
        sets x reps @ weight
        sets x reps @ weight
        ...

        Weight references the editable 1RM cell.
        """

        phase_name = display_phase(phase)

        pieces = [
            f'"{phase_name}"'
        ]

        workout = self.get_workout_template(
            phase
        )

        for percentage, reps, sets in workout:

            pieces.append(
                "CHAR(10)"
            )

            pieces.append(
                f'"{sets} x {reps} @ "'
            )

            pieces.append(
                f"ROUNDUP({one_rep_max_cell}*{percentage},0)"
            )

        return "=" + "&".join(pieces)

    # ========================================================
    # CREATE EXCEL
    # ========================================================

    def create_excel(
        self,
        filename="workout.xlsx",
        n_weeks=10,
    ):

        wb = Workbook()

        plan = wb.active
        plan.title = "Workout Plan"

        # ----------------------------------------------------
        # 1RM INPUT AREA
        # ----------------------------------------------------

        plan["A1"] = "ONE REP MAX"

        for col, lift in enumerate(
            LIFTS,
            start=2,
        ):

            plan.cell(
                row=1,
                column=col,
                value=lift.title(),
            )

            plan.cell(
                row=2,
                column=col,
                value=self.current_one_rep_max[lift],
            )

        plan["A2"] = "1RM"

        # ----------------------------------------------------
        # WORKOUT TABLE
        # ----------------------------------------------------

        header_row = 4

        plan.cell(
            row=header_row,
            column=1,
            value="Week",
        )

        for col, lift in enumerate(
            LIFTS,
            start=2,
        ):

            plan.cell(
                row=header_row,
                column=col,
                value=lift.title(),
            )

        first_week = self.this_monday()

        for i in range(n_weeks):

            excel_row = header_row + 1 + i

            week = (
                first_week
                + timedelta(weeks=i)
            )

            plan.cell(
                row=excel_row,
                column=1,
                value=week,
            )

            plan.cell(
                row=excel_row,
                column=1,
            ).number_format = "yyyy-mm-dd"

            for col, lift in enumerate(
                LIFTS,
                start=2,
            ):

                phase = self.get_phase(
                    lift,
                    week,
                )

                # B2, C2, D2, E2
                orm_cell = (
                    f"${get_column_letter(col)}$2"
                )

                formula = self.workout_excel_formula(
                    phase,
                    orm_cell,
                )

                plan.cell(
                    row=excel_row,
                    column=col,
                    value=formula,
                )

        # ----------------------------------------------------
        # FORMATTING
        # ----------------------------------------------------

        for cell in plan[1]:
            cell.font = Font(bold=True)

        for cell in plan[header_row]:
            cell.font = Font(bold=True)

        plan.freeze_panes = "B5"

        plan.column_dimensions["A"].width = 14

        for col in range(2, 6):

            letter = get_column_letter(col)

            plan.column_dimensions[
                letter
            ].width = 30

        for row in range(
            header_row + 1,
            header_row + n_weeks + 1,
        ):

            plan.row_dimensions[row].height = 100

            for col in range(2, 6):

                plan.cell(
                    row=row,
                    column=col,
                ).alignment = Alignment(
                    wrap_text=True,
                    vertical="top",
                )

        # ====================================================
        # SETTINGS SHEET
        # ====================================================

        settings = wb.create_sheet(
            "Settings"
        )

        settings.append([
            "Setting",
            "Value",
        ])

        settings.append([
            "Starting Week",
            self.starting_week["week"],
        ])

        settings.append([])

        settings.append([
            "Lift",
            "Starting Phase",
        ])

        for lift in LIFTS:

            settings.append([
                lift,
                self.starting_week[lift],
            ])

        settings.append([])
        settings.append([
            "1RM values are editable in",
            "Workout Plan row 2",
        ])

        settings.column_dimensions["A"].width = 25
        settings.column_dimensions["B"].width = 30

        settings["A1"].font = Font(bold=True)
        settings["B1"].font = Font(bold=True)

        settings["A4"].font = Font(bold=True)
        settings["B4"].font = Font(bold=True)

        # ----------------------------------------------------
        # SAVE
        # ----------------------------------------------------

        wb.save(filename)

        print(
            f"Saved Excel workout plan: {filename}"
        )

    # ========================================================
    # LOAD FROM EXCEL
    # ========================================================

    @classmethod
    def from_excel(cls, filename):

        wb = load_workbook(
            filename,
            data_only=False,
        )

        plan = wb["Workout Plan"]
        settings = wb["Settings"]

        # ----------------------------------------------------
        # Read 1RM
        # ----------------------------------------------------

        one_rep_max = {}

        for col, lift in enumerate(
            LIFTS,
            start=2,
        ):

            one_rep_max[lift] = (
                plan.cell(
                    row=2,
                    column=col,
                ).value
            )

        # ----------------------------------------------------
        # Read starting schedule
        # ----------------------------------------------------

        starting_week = {
            "week": settings["B2"].value,
        }

        for row in range(5, 9):

            lift = settings.cell(
                row=row,
                column=1,
            ).value

            phase = settings.cell(
                row=row,
                column=2,
            ).value

            starting_week[lift] = phase

        return cls(
            current_one_rep_max=one_rep_max,
            starting_week=starting_week,
        )


# ============================================================
# EXAMPLE
# ============================================================

if __name__ == "__main__":

    program = Program(

        current_one_rep_max={
            "bench": 100,
            "squat": 140,
            "deadlift": 180,
            "press": 60,
        },

        starting_week={
            "week": "2026-09-28",

            "bench":
                "fives_realization",

            "squat":
                "threes_intensification",

            "deadlift":
                "threes_deload",

            "press":
                "tens_accumulation",
        },
    )

    # --------------------------------------------------------
    # This week's complete workouts
    # --------------------------------------------------------

    program.print_this_week()

    # --------------------------------------------------------
    # Next 10 weeks: phase overview
    # --------------------------------------------------------

    program.print_overview(
        n_weeks=10
    )

    # --------------------------------------------------------
    # Create 10-week Excel workbook
    # --------------------------------------------------------

    program.create_excel(
        "juggernaut.xlsx",
        n_weeks=10,
    )

    # --------------------------------------------------------
    # Change 1RM from Python
    # --------------------------------------------------------

    program.set_one_rep_max(
        "bench",
        105,
    )

    program.set_one_rep_maxes(
        squat=150,
        deadlift=190,
    )

    # --------------------------------------------------------
    # Load 1RM + schedule back from Excel
    # --------------------------------------------------------

    program2 = Program.from_excel(
        "/home/will/code/workout/juggernaut.xlsx"
    )

    program2.print_this_week()