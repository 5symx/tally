#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <signal.h>

/**
 * @brief Launches a client program with LD_PRELOAD set.
 *
 * @param program_path The path to the client executable.
 */
void launch_client_with_trace(const char *program_path) {
    // Set the LD_PRELOAD environment variable to preload our tracing library.
    // The "1" indicates that we want to overwrite the variable if it already exists.
    if (setenv("LD_PRELOAD", "./libclient.so", 1) != 0) {
        perror("Failed to set LD_PRELOAD environment variable");
        exit(EXIT_FAILURE);
    }

    // Announce the launch of the client program.
    printf("Launching client: %s with LD_PRELOAD=./libclient.so\n", program_path);

    // The execlp function replaces the current process image with a new one.
    // It searches for the program in the system's PATH.
    // We pass the program path as the first and second argument, followed by a NULL terminator.
    execlp(program_path, program_path, (char *)NULL);

    // If execlp returns, it means an error occurred.
    perror("Failed to execute client program");
    exit(EXIT_FAILURE);
}

int main() {
    pid_t server_pid;

    // Fork the process to create a child for the server.
    server_pid = fork();

    if (server_pid < 0) {
        perror("Failed to fork for server");
        exit(EXIT_FAILURE);
    }

    if (server_pid == 0) {
        // This is the child process, which will become the server.
        printf("Starting server...\n");
        execlp("./my_server", "./my_server", (char *)NULL);

        // If execlp returns, an error has occurred.
        perror("Failed to execute server program");
        exit(EXIT_FAILURE);
    }

    // This is the parent process.
    printf("Server started with PID: %d\n", server_pid);

    // A brief pause to allow the server to initialize before clients connect.
    sleep(2);

    // An array of client programs to be launched.
    const char *client_programs[] = {"./program_A", "./program_B", "./program_C"};
    int num_clients = sizeof(client_programs) / sizeof(client_programs[0]);
    pid_t client_pids[num_clients];

    // Loop to fork and launch each client program.
    for (int i = 0; i < num_clients; i++) {
        client_pids[i] = fork();

        if (client_pids[i] < 0) {
            perror("Failed to fork for client");
            // Terminate the already started server before exiting.
            kill(server_pid, SIGTERM);
            exit(EXIT_FAILURE);
        }

        if (client_pids[i] == 0) {
            // This is the child process for the client.
            launch_client_with_trace(client_programs[i]);
        }
    }

    // Wait for all client processes to complete.
    for (int i = 0; i < num_clients; i++) {
        int status;
        waitpid(client_pids[i], &status, 0);
        printf("Client program %s has finished.\n", client_programs[i]);
    }

    // After all clients have finished, terminate the server process.
    printf("All clients have finished. Terminating server.\n");
    kill(server_pid, SIGTERM);

    return 0;
}