#include <stdio.h>
#include <wiringPi.h>
#include <stdbool.h>
#include <time.h>
#include <unistd.h>

int main(void)
{
    // Switch: Physical pin 31, BCM GPIO6, and WiringPi pin 22.
    const int givare1 = 4;
    const int givare2 = 5;
    bool counted = false;

    int countcm = 0;
    int oldcount = 0;
    int calib = 65000; //micrometer

    wiringPiSetup();

    pinMode(givare1, INPUT);
    pinMode(givare2, INPUT);

    while (1) {
        FILE * givarna;
        oldcount = countcm;

        if ((digitalRead(givare2) == HIGH) && (digitalRead(givare1) == HIGH) && (counted == true)) {
            counted = false;
            usleep(5);
        }

        else if ((digitalRead(givare1) == LOW) && (digitalRead(givare2) == HIGH) && (counted == false)) {
            countcm = countcm + calib;
            counted = true;
            usleep(5);
        }

        else if ((digitalRead(givare1) == HIGH) && (digitalRead(givare2) == LOW) && (counted == false)) {
            countcm = countcm - calib;
            counted = true;
            usleep(5);
        }

        if (oldcount != countcm) {
            printf("%d\n", countcm);
            givarna = fopen("/dev/shm/givarna","w+");
            fprintf(givarna, "%d", countcm);
            fclose(givarna);
        }
        usleep(1);
    }
    return 0;
}
