We have provided a python script to run your program on the provided training problems. You are not required to use this, but you might find it helpful in validating your submission. Recall, your program should accept a command line argument containing a path to a problem in the format described in the prompt.

To use the evaluation script, run the following in a shell:

python3 evaluateShared.py --cmd {command to run your program} --problemDir {folder containing training problems}

The script will load every problem in the training problem folder, and run the command on each file. The {command to run your program} should NOT include a file directory (as these will be read from the problemDir folder).

For example, if your solution is a python3 script called "mySubmission.py", and you have downloaded the training problems to a folder called "trainingProblems", then run

python3 evaluateShared.py --cmd "python3 mySubmission.py" --problemDir trainingProblems

(Quotes are needed around "python3 mySubmission.py" because of the space.) If your solution is a compiled executable called "mySubmission", then it would be

python3 evaluateShared.py --cmd ./mySubmission --problemDir trainingProblems

The script will check your program for errors and print your score on each problem.


python evaluateShared.py --cmd "python vrp.py" --problemDir "test_data"

Cheapest:
    mean cost: 56484.8752497138
    mean run time: 64.58051204681396ms

Closest:
    mean cost: 47963.81284400135
    mean run time: 73.84626865386963ms

Furthest from depot:
    mean cost: 47894.524588592176
    mean run time: 77.5111198425293ms

Closest to depot:
    mean cost: 55610.08419697672
    mean run time: 76.62986516952515ms