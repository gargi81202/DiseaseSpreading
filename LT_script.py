import subprocess

def run_command(command):
    try:
        result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing command '{command}': {e.stderr}")
        return e.returncode

    outputs = result.stdout.strip().splitlines()
    numeric_outputs = []
    
    for output in outputs:
        output = output.strip()
        try:
            # Try to convert to float
            numeric_value = float(output)
            
            # If the value is a whole number (like 3.0), convert it to an integer
            if numeric_value.is_integer():
                numeric_outputs.append(int(numeric_value))
            else:
                numeric_outputs.append(numeric_value)  # Keep it as a float if it's not an integer
        except ValueError:
            print(f"Output is not a valid number: '{output}'")
            return None  # Or handle as appropriate

    return numeric_outputs  # Return the list of numbers (ints and floats)

if __name__ == "__main__":
    # Define the three commands you want to run
    # command1 = "python3 LT_generate_ERG.py"
    command1 = "g++ -o TS linear_threshold_tabu_search.cpp"
    run_command(command1)
    graph_file = input("graph file name (eg: LT_waxman_gaussian_example.txt) = ")
    command2 = f"./TS {graph_file}"  # Example: list files in the current directory
    # command3 = "./linear_threshold_greedy ERG_example.txt"

    local_search_avg = 0
    greedy_avg = 0
    hill_climbing_average = 0
    greedy_time = 0
    local_search_time = 0
    hill_climbing_time = 0
    for i in range(1):
        # Run the commands sequentially
        # run_command(command1)
        arr = run_command(command2)
        # print('-------')
        # print(arr[0], arr[1])
        # print('-------')
        greedy_time += arr[0]
        greedy_avg += arr[1]
        local_search_time += arr[2]
        local_search_avg += arr[3]
        hill_climbing_time += arr[4]
        hill_climbing_average += arr[5]
    num_instances = int(input("num instances = "))
    outputfilename = "output_" + graph_file
    with open(outputfilename, 'a') as file:
        # Calculate the values
        greedy_avg_result = greedy_avg / (1 * num_instances)
        local_search_avg_result = local_search_avg / (1 * num_instances)
        hill_climbing_avg_result = hill_climbing_average / (1 * num_instances)

        # Create the formatted strings
        greedy_avg_str = f"Greedy average: {greedy_avg_result}\n"
        local_search_avg_str = f"Local search average: {local_search_avg_result}\n"
        hill_climbing_avg_str = f"Hill climbing average: {hill_climbing_avg_result}\n"
        greedy_time_str = f"Greedy time taken: {greedy_time}\n"
        local_search_time_str = f"Local search time taken: {local_search_time}\n"
        hill_climbing_time_str = f"Hill climbing time taken: {hill_climbing_time}\n"

        # Print to console
        print(greedy_avg_str)
        print(greedy_time_str)
        print(local_search_avg_str)
        print(local_search_time_str)
        print(hill_climbing_avg_str)
        print(hill_climbing_time_str)
        # Write to the file
        file.write(greedy_avg_str)
        file.write(greedy_time_str)
        file.write(local_search_avg_str)
        file.write(local_search_time_str)
        file.write(hill_climbing_avg_str)
        file.write(hill_climbing_time_str)
