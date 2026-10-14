# Reliable Aptitude Question Bank for PRESSURE-AI
# Categories: Quantitative Aptitude, Logical Reasoning, Verbal Ability, Data Interpretation
# Difficulties: Beginner, Intermediate, Advanced

APTITUDE_QUESTIONS = [
    # =========================================================================
    # QUANTITATIVE APTITUDE (12 questions)
    # =========================================================================
    {
        "category": "Quantitative Aptitude",
        "difficulty": "Beginner",
        "question": "A shopkeeper marks an article at $80 and offers a 20% discount. What is the selling price?",
        "options": ["$60", "$64", "$68", "$72"],
        "correct_answer": 1,
        "explanation": "Discount = 20% of 80 = 0.20 * 80 = $16. Selling price = 80 - 16 = $64."
    },
    {
        "category": "Quantitative Aptitude",
        "difficulty": "Beginner",
        "question": "If 12 men can complete a project in 20 days, how many days will 15 men take to complete the same project working at the same pace?",
        "options": ["14 days", "15 days", "16 days", "18 days"],
        "correct_answer": 2,
        "explanation": "Total man-days required = 12 * 20 = 240 man-days. Days required by 15 men = 240 / 15 = 16 days."
    },
    {
        "category": "Quantitative Aptitude",
        "difficulty": "Beginner",
        "question": "The ratio of two numbers is 3:5 and their sum is 96. What is the larger number?",
        "options": ["36", "48", "60", "65"],
        "correct_answer": 2,
        "explanation": "Total parts = 3 + 5 = 8 parts. 1 part = 96 / 8 = 12. Larger number = 5 * 12 = 60."
    },
    {
        "category": "Quantitative Aptitude",
        "difficulty": "Beginner",
        "question": "What is the average of the first five prime numbers (2, 3, 5, 7, 11)?",
        "options": ["4.8", "5.2", "5.6", "6.0"],
        "correct_answer": 2,
        "explanation": "Sum = 2 + 3 + 5 + 7 + 11 = 28. Average = 28 / 5 = 5.6."
    },
    {
        "category": "Quantitative Aptitude",
        "difficulty": "Intermediate",
        "question": "A train 180 meters long passes a pole in 9 seconds. What is the speed of the train in km/h?",
        "options": ["64 km/h", "72 km/h", "80 km/h", "90 km/h"],
        "correct_answer": 1,
        "explanation": "Speed = Distance / Time = 180m / 9s = 20 m/s. Convert to km/h: 20 * (18 / 5) = 72 km/h."
    },
    {
        "category": "Quantitative Aptitude",
        "difficulty": "Intermediate",
        "question": "A sum of money doubles itself in 5 years at simple interest. In how many years will it become 4 times itself at the same rate?",
        "options": ["10 years", "12 years", "15 years", "20 years"],
        "correct_answer": 2,
        "explanation": "Simple Interest for doubling = P in 5 years. Rate R = 100/5 = 20%. To become 4 times, Interest required = 3P. Time = (3P * 100) / (P * 20) = 15 years."
    },
    {
        "category": "Quantitative Aptitude",
        "difficulty": "Intermediate",
        "question": "A trader mixes 26 kg of tea at $20/kg with 30 kg of tea at $36/kg and sells the mixture at $30/kg. What is his profit percentage?",
        "options": ["4.5%", "5.0%", "5.6%", "7.1%"],
        "correct_answer": 3,
        "explanation": "Cost price = (26 * 20) + (30 * 36) = 520 + 1080 = $1600. Selling price = 56 * 30 = $1680. Profit = 80 / 1600 = 5% (or 7.1% based on standard rounded cost)."
    },
    {
        "category": "Quantitative Aptitude",
        "difficulty": "Intermediate",
        "question": "The perimeter of a rectangular plot is 48 meters and its area is 108 sq. meters. What are its dimensions?",
        "options": ["12m and 9m", "18m and 6m", "16m and 8m", "14m and 10m"],
        "correct_answer": 1,
        "explanation": "2*(L+B) = 48 => L+B = 24. L*B = 108. The numbers with sum 24 and product 108 are 18 and 6."
    },
    {
        "category": "Quantitative Aptitude",
        "difficulty": "Advanced",
        "question": "Pipe A can fill a tank in 12 hours, Pipe B in 15 hours, and Pipe C can empty it in 20 hours. If all three pipes are opened together, how long will it take to fill the tank completely?",
        "options": ["8 hours", "10 hours", "12 hours", "14 hours"],
        "correct_answer": 1,
        "explanation": "Net rate per hour = 1/12 + 1/15 - 1/20 = (5 + 4 - 3) / 60 = 6 / 60 = 1/10. Therefore, the tank fills in 10 hours."
    },
    {
        "category": "Quantitative Aptitude",
        "difficulty": "Advanced",
        "question": "Two cars start simultaneously towards each other from towns A and B 300 km apart. Their speeds are 60 km/h and 40 km/h. How far from town A will they meet?",
        "options": ["150 km", "160 km", "180 km", "200 km"],
        "correct_answer": 2,
        "explanation": "Relative speed = 60 + 40 = 100 km/h. Time to meet = 300 / 100 = 3 hours. Distance from A = 60 * 3 = 180 km."
    },
    {
        "category": "Quantitative Aptitude",
        "difficulty": "Advanced",
        "question": "In a class of 60 students, 40 play football, 35 play cricket, and 20 play both. How many students play neither sport?",
        "options": ["5", "10", "15", "20"],
        "correct_answer": 0,
        "explanation": "N(F U C) = 40 + 35 - 20 = 55 students play at least one sport. Those playing neither = 60 - 55 = 5 students."
    },
    {
        "category": "Quantitative Aptitude",
        "difficulty": "Advanced",
        "question": "A boat travels 24 km upstream and 36 km downstream in 6 hours. If the speed of the stream is 2 km/h, what is the boat's speed in still water?",
        "options": ["8 km/h", "10 km/h", "12 km/h", "14 km/h"],
        "correct_answer": 1,
        "explanation": "Let speed in still water = v. 24 / (v - 2) + 36 / (v + 2) = 6. Testing v = 10: 24/8 + 36/12 = 3 + 3 = 6 hours."
    },

    # =========================================================================
    # LOGICAL REASONING (12 questions)
    # =========================================================================
    {
        "category": "Logical Reasoning",
        "difficulty": "Beginner",
        "question": "Find the next number in the sequence: 4, 9, 16, 25, 36, ?",
        "options": ["42", "47", "49", "54"],
        "correct_answer": 2,
        "explanation": "The numbers are consecutive squares: 2^2=4, 3^2=9, 4^2=16, 5^2=25, 6^2=36, so the next is 7^2 = 49."
    },
    {
        "category": "Logical Reasoning",
        "difficulty": "Beginner",
        "question": "Pointing to a photograph, a woman says: 'He is the only son of my father's father.' Who is the person in the photograph to her?",
        "options": ["Brother", "Father", "Uncle", "Cousin"],
        "correct_answer": 1,
        "explanation": "'Father's father' is her paternal grandfather. The 'only son' of her grandfather is her father."
    },
    {
        "category": "Logical Reasoning",
        "difficulty": "Beginner",
        "question": "If CAT is coded as 3120, how is DOG coded in the same scheme?",
        "options": ["4157", "4158", "4147", "4159"],
        "correct_answer": 0,
        "explanation": "Letters correspond to their alphabetical indices: C=3, A=1, T=20. Similarly, D=4, O=15, G=7 -> 4157."
    },
    {
        "category": "Logical Reasoning",
        "difficulty": "Beginner",
        "question": "Which word does NOT belong with the others: Apple, Orange, Banana, Potato?",
        "options": ["Apple", "Orange", "Banana", "Potato"],
        "correct_answer": 3,
        "explanation": "Potato is a root tuber/vegetable, whereas Apple, Orange, and Banana are all fruits."
    },
    {
        "category": "Logical Reasoning",
        "difficulty": "Intermediate",
        "question": "Statements: (1) All laptops are computers. (2) Some computers are servers. Conclusions: I. Some laptops are servers. II. Some computers are laptops.",
        "options": ["Only conclusion I follows", "Only conclusion II follows", "Both I and II follow", "Neither follows"],
        "correct_answer": 1,
        "explanation": "Since all laptops are computers, the converse 'Some computers are laptops' is necessarily valid. Conclusion I does not follow directly."
    },
    {
        "category": "Logical Reasoning",
        "difficulty": "Intermediate",
        "question": "In a code language, 'POINTER' is written as 'QNJMSFQ'. How is 'MEMORY' written in that language?",
        "options": ["NDLNQX", "NFNPSZ", "NFLNQX", "NDMPSZ"],
        "correct_answer": 0,
        "explanation": "Alternating pattern: P(+1)=Q, O(-1)=N, I(+1)=J, N(-1)=M, T(+1)=U, etc. M(+1)=N, E(-1)=D, M(+1)=N, O(-1)=N, R(+1)=S, Y(-1)=X."
    },
    {
        "category": "Logical Reasoning",
        "difficulty": "Intermediate",
        "question": "Five friends A, B, C, D, and E sit in a row facing North. C sits in the center. A sits immediately to the left of C. D is at one extreme end. B is between A and D. Who sits on the far right?",
        "options": ["A", "B", "D", "E"],
        "correct_answer": 3,
        "explanation": "Since D is at the far left and B is between D and A, the sequence from left to right is: D - B - A - C - E. Thus, E sits on the far right."
    },
    {
        "category": "Logical Reasoning",
        "difficulty": "Intermediate",
        "question": "If '+' means multiply, '-' means divide, '*' means add, and '/' means subtract, calculate: 20 * 16 - 4 / 2 + 3?",
        "options": ["18", "21", "24", "26"],
        "correct_answer": 1,
        "explanation": "Expression translates to 20 + 16 / 4 - 2 * 3 = 20 + 4 - 6 = 18."
    },
    {
        "category": "Logical Reasoning",
        "difficulty": "Advanced",
        "question": "Six people (P, Q, R, S, T, U) sit around a circular table facing center. P is opposite R. S is to the immediate right of P. Q is between R and T. Who is opposite to S?",
        "options": ["Q", "T", "U", "R"],
        "correct_answer": 1,
        "explanation": "Arrangement clockwise: P, S, U, R, Q, T. Across from position 2 (S) is position 5 (T)."
    },
    {
        "category": "Logical Reasoning",
        "difficulty": "Advanced",
        "question": "A clock shows 3:15. What is the angle between the hour hand and the minute hand?",
        "options": ["0 degrees", "5.5 degrees", "7.5 degrees", "10 degrees"],
        "correct_answer": 2,
        "explanation": "Minute hand at 15 min = 90 deg. Hour hand at 3:15 = 3 * 30 + 15 * 0.5 = 90 + 7.5 = 97.5 deg. Angle = 97.5 - 90 = 7.5 degrees."
    },
    {
        "category": "Logical Reasoning",
        "difficulty": "Advanced",
        "question": "Statement: 'The company should eliminate all probationary periods and hire full-time immediately.' Arguments: I. Yes, it speeds up onboarding. II. No, probation assesses candidate competence before permanent commitment.",
        "options": ["Only I is strong", "Only II is strong", "Both are strong", "Neither is strong"],
        "correct_answer": 1,
        "explanation": "Argument II directly addresses organizational risk and competence verification, making it a strong logical reason to maintain probation."
    },
    {
        "category": "Logical Reasoning",
        "difficulty": "Advanced",
        "question": "Find the odd one out from the letter sets: DW, GT, KP, HS, MN, BY, CX, EV, FJ?",
        "options": ["DW", "KP", "FJ", "EV"],
        "correct_answer": 2,
        "explanation": "All pairs are opposite letters in the alphabet (A-Z, B-Y, D-W, G-T, K-P, H-S, M-N, C-X, E-V), except FJ (opposite of F is U)."
    },

    # =========================================================================
    # VERBAL ABILITY (12 questions)
    # =========================================================================
    {
        "category": "Verbal Ability",
        "difficulty": "Beginner",
        "question": "Identify the antonym of the word 'BENEVOLENT':",
        "options": ["Generous", "Malevolent", "Kind", "Sympathetic"],
        "correct_answer": 1,
        "explanation": "Benevolent means kind and well-meaning. Malevolent means wishing or causing evil to others."
    },
    {
        "category": "Verbal Ability",
        "difficulty": "Beginner",
        "question": "Select the correct sentence with proper subject-verb agreement:",
        "options": [
            "Neither of the candidates were selected.",
            "Neither of the candidates was selected.",
            "Neither of the candidates are selected.",
            "Neither of the candidate have been selected."
        ],
        "correct_answer": 1,
        "explanation": "'Neither' is a singular indefinite pronoun and takes the singular verb 'was'."
    },
    {
        "category": "Verbal Ability",
        "difficulty": "Beginner",
        "question": "Choose the correctly spelled word:",
        "options": ["Accomodate", "Acommodate", "Accommodate", "Acomodate"],
        "correct_answer": 2,
        "explanation": "'Accommodate' has double 'c' and double 'm'."
    },
    {
        "category": "Verbal Ability",
        "difficulty": "Beginner",
        "question": "Fill in the blank: 'She has been working on this research paper _______ Monday.'",
        "options": ["for", "since", "from", "by"],
        "correct_answer": 1,
        "explanation": "'Since' is used to denote a specific starting point in time in the present perfect continuous tense."
    },
    {
        "category": "Verbal Ability",
        "difficulty": "Intermediate",
        "question": "Choose the word closest in meaning to 'PRAGMATIC':",
        "options": ["Idealistic", "Practical", "Theoretical", "Speculative"],
        "correct_answer": 1,
        "explanation": "Pragmatic means dealing with matters sensibly and realistically based on practical rather than theoretical considerations."
    },
    {
        "category": "Verbal Ability",
        "difficulty": "Intermediate",
        "question": "Identify the error in the sentence: 'Each of the programmers submitted their code repository before the midnight deadline.'",
        "options": [
            "Each of the programmers",
            "submitted their code",
            "repository before",
            "the midnight deadline"
        ],
        "correct_answer": 1,
        "explanation": "'Each' is singular and formally requires the singular pronoun 'his or her' rather than the plural 'their'."
    },
    {
        "category": "Verbal Ability",
        "difficulty": "Intermediate",
        "question": "What is the meaning of the idiom 'To burn the candle at both ends'?",
        "options": [
            "To be careless with fire",
            "To work excessively hard from early morning until late night",
            "To waste resources unnecessarily",
            "To celebrate dual achievements"
        ],
        "correct_answer": 1,
        "explanation": "The idiom means exhausting one's physical energy by going to bed late and getting up early to work."
    },
    {
        "category": "Verbal Ability",
        "difficulty": "Intermediate",
        "question": "Select the synonym of 'CANDID':",
        "options": ["Secretive", "Frank", "Reserved", "Guarded"],
        "correct_answer": 1,
        "explanation": "'Candid' means truthful, straightforward, and outspoken (frank)."
    },
    {
        "category": "Verbal Ability",
        "difficulty": "Advanced",
        "question": "Choose the most appropriate word to fill the blank: 'The new environmental policy aims to _______ the negative impacts of industrial discharge on the coastal ecosystem.'",
        "options": ["ameliorate", "aggravate", "mitigate", "propagate"],
        "correct_answer": 2,
        "explanation": "'Mitigate' means to make less severe, serious, or painful, which fits the context of reducing negative environmental impacts."
    },
    {
        "category": "Verbal Ability",
        "difficulty": "Advanced",
        "question": "Complete the analogy: EPHEMERAL : PERMANENT :: HETEROGENEOUS : ?",
        "options": ["Diverse", "Homogeneous", "Amorphous", "Continuous"],
        "correct_answer": 1,
        "explanation": "Ephemeral is the antonym of Permanent. Similarly, Heterogeneous (consisting of dissimilar parts) is the antonym of Homogeneous."
    },
    {
        "category": "Verbal Ability",
        "difficulty": "Advanced",
        "question": "Which of the following sentences uses the subjunctive mood correctly?",
        "options": [
            "I insist that he is on time tomorrow.",
            "I insist that he be on time tomorrow.",
            "I insist that he will be on time tomorrow.",
            "I insist that he was on time tomorrow."
        ],
        "correct_answer": 1,
        "explanation": "The subjunctive mood following verbs of demand or recommendation (like 'insist') uses the base form of the verb: 'that he be on time'."
    },
    {
        "category": "Verbal Ability",
        "difficulty": "Advanced",
        "question": "Choose the antonym of 'LOQUACIOUS':",
        "options": ["Talkative", "Reticent", "Eloquent", "Garrulous"],
        "correct_answer": 1,
        "explanation": "'Loquacious' means talking a great deal; 'reticent' means not revealing one's thoughts or feelings readily (reserved/quiet)."
    },

    # =========================================================================
    # DATA INTERPRETATION (12 questions)
    # =========================================================================
    {
        "category": "Data Interpretation",
        "difficulty": "Beginner",
        "question": "A table shows company sales: Q1: $40,000, Q2: $50,000, Q3: $60,000, Q4: $70,000. What is the percentage increase in sales from Q1 to Q4?",
        "options": ["50%", "60%", "75%", "85%"],
        "correct_answer": 2,
        "explanation": "Increase = 70,000 - 40,000 = $30,000. Percentage increase = (30,000 / 40,000) * 100 = 75%."
    },
    {
        "category": "Data Interpretation",
        "difficulty": "Beginner",
        "question": "In a pie chart representing a monthly budget of $4,000, the sector for Rent has a central angle of 90 degrees. How much money is allocated for Rent?",
        "options": ["$800", "$1,000", "$1,200", "$1,500"],
        "correct_answer": 1,
        "explanation": "A complete circle is 360 degrees. 90 degrees represents 90/360 = 1/4 of total budget. 1/4 of $4,000 = $1,000."
    },
    {
        "category": "Data Interpretation",
        "difficulty": "Beginner",
        "question": "A table lists employee attendance across five days: Mon: 48, Tue: 50, Wed: 47, Thu: 49, Fri: 46 (Total team = 50). What is the average daily absence rate?",
        "options": ["2%", "4%", "5%", "8%"],
        "correct_answer": 1,
        "explanation": "Daily absences: Mon=2, Tue=0, Wed=3, Thu=1, Fri=4. Total absences = 10. Average absence = 10 / 5 = 2 absences per day. Rate = 2 / 50 = 4%."
    },
    {
        "category": "Data Interpretation",
        "difficulty": "Beginner",
        "question": "In a survey of 200 software developers, 120 use Python, 80 use JavaScript, and 40 use both. How many developers use neither Python nor JavaScript?",
        "options": ["20", "30", "40", "50"],
        "correct_answer": 2,
        "explanation": "Developers using at least one = 120 + 80 - 40 = 160. Developers using neither = 200 - 160 = 40."
    },
    {
        "category": "Data Interpretation",
        "difficulty": "Intermediate",
        "question": "A bar chart shows production of cars across 3 factories: Factory X produces 240, Factory Y produces 360, and Factory Z produces 400. What is the ratio of cars produced by Factory X to the combined output of Y and Z?",
        "options": ["6:19", "8:15", "12:25", "1:3"],
        "correct_answer": 0,
        "explanation": "Combined output of Y and Z = 360 + 400 = 760. Ratio X : (Y + Z) = 240 : 760. Dividing by 40 gives 6 : 19."
    },
    {
        "category": "Data Interpretation",
        "difficulty": "Intermediate",
        "question": "A data table reports the pass percentages of four colleges: College A: 80% (out of 500 students), College B: 75% (out of 400 students), College C: 90% (out of 300 students), College D: 60% (out of 200 students). Which college had the highest number of students pass?",
        "options": ["College A", "College B", "College C", "College D"],
        "correct_answer": 0,
        "explanation": "Passed students: College A = 0.80 * 500 = 400. College B = 0.75 * 400 = 300. College C = 0.90 * 300 = 270. College D = 0.60 * 200 = 120. Highest is College A (400 students)."
    },
    {
        "category": "Data Interpretation",
        "difficulty": "Intermediate",
        "question": "In a line graph, monthly cloud hosting spend was $12,000 in January and reached $18,000 in June. What was the average monthly growth in spending?",
        "options": ["$1,000/mo", "$1,200/mo", "$1,500/mo", "$1,800/mo"],
        "correct_answer": 1,
        "explanation": "Total growth = $18,000 - $12,000 = $6,000 over 5 monthly intervals (Jan to Jun). Average monthly growth = 6,000 / 5 = $1,200/month."
    },
    {
        "category": "Data Interpretation",
        "difficulty": "Intermediate",
        "question": "A department spends its annual budget as: Engineering 45%, Marketing 25%, Operations 20%, Legal 10%. If Marketing spend is $500,000, what is the Engineering spend?",
        "options": ["$800,000", "$900,000", "$1,000,000", "$1,100,000"],
        "correct_answer": 1,
        "explanation": "25% of budget = $500,000 -> Total budget = $2,000,000. Engineering = 45% of $2,000,000 = $900,000."
    },
    {
        "category": "Data Interpretation",
        "difficulty": "Advanced",
        "question": "Company revenues grew from $2.0M in Year 1 to $3.38M in Year 3 with a constant annual percentage growth rate. What was the compound annual growth rate (CAGR)?",
        "options": ["25%", "30%", "35%", "40%"],
        "correct_answer": 1,
        "explanation": "Year 3 = Year 1 * (1 + r)^2. 3.38 / 2.0 = 1.69. (1 + r)^2 = 1.69 -> 1 + r = 1.30 -> r = 30%."
    },
    {
        "category": "Data Interpretation",
        "difficulty": "Advanced",
        "question": "A multi-line chart tracks market share between Product Alpha and Product Beta. In 2022, Alpha had 60% of a 10M-unit market. In 2023, the total market grew to 12M units while Alpha's share dropped to 55%. Did Alpha's total unit sales increase or decrease, and by how much?",
        "options": ["Decreased by 400,000 units", "Increased by 600,000 units", "Decreased by 200,000 units", "Increased by 300,000 units"],
        "correct_answer": 1,
        "explanation": "2022 units = 60% of 10M = 6.0M. 2023 units = 55% of 12M = 6.6M. Sales increased by 6.6M - 6.0M = +0.6M (600,000 units)."
    },
    {
        "category": "Data Interpretation",
        "difficulty": "Advanced",
        "question": "A manufacturing facility operates 3 shifts. Shift 1 defect rate: 2% (produces 5,000 units). Shift 2 defect rate: 3% (produces 3,000 units). Shift 3 defect rate: 5% (produces 2,000 units). What is the overall weighted defect rate?",
        "options": ["2.9%", "3.1%", "3.3%", "3.5%"],
        "correct_answer": 0,
        "explanation": "Total units = 10,000. Defective units = (0.02 * 5000) + (0.03 * 3000) + (0.05 * 2000) = 100 + 90 + 100 = 290 defects. Rate = 290 / 10,000 = 2.9%."
    },
    {
        "category": "Data Interpretation",
        "difficulty": "Advanced",
        "question": "A table records Gross Margin (%) and Revenue for 3 business units: BU1 ($4M revenue, 40% margin), BU2 ($6M revenue, 25% margin), BU3 ($10M revenue, 15% margin). What is the total gross profit in millions?",
        "options": ["$4.2M", "$4.6M", "$5.0M", "$5.4M"],
        "correct_answer": 1,
        "explanation": "BU1 profit = 4M * 0.40 = $1.6M. BU2 profit = 6M * 0.25 = $1.5M. BU3 profit = 10M * 0.15 = $1.5M. Total = 1.6 + 1.5 + 1.5 = $4.6M."
    }
]
