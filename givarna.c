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
    bool counted = true;
    int rp;
    int rp_array[2] = (5,5);

    long countcm = 0;
    long oldcount = 0;
    //int calib = 65750; //micrometer
    int calib = 98600; //micrometer

    wiringPiSetup();

    pinMode(givare1, INPUT);
    pinMode(givare2, INPUT);
    pullUpDnControl(givare1, PUD_DOWN);
    pullUpDnControl(givare2, PUD_DOWN);

    while (1) {
        oldcount = countcm;
        rp_array[1] = rp;
        if ((digitalRead(givare2) == HIGH) && (digitalRead(givare1) == HIGH) && (counted == true)) {
            counted = false;
            rp = 0;
            usleep(1);
        }
        else if ((digitalRead(givare2) == LOW) && (digitalRead(givare1) == LOW) && (counted == true)) {
            counted = false;
            rp = 2;
            usleep(1);
        }
        else if ((digitalRead(givare1) == LOW) && (digitalRead(givare2) == HIGH) && (counted == true)) {
            counted = false;
            rp = 1;
            usleep(1);
        }
        else if ((digitalRead(givare1) == HIGH) && (digitalRead(givare2) == LOW) && (counted == true)) {
            counted = false;
            rp = 3;
            usleep(1);
        }
        rp_array[0] = rp;
        if ((rp_array == (0,3)) || (rp_array == (3,2)) || (rp_array == (2,1)) || (rp_array == (1,0))) {
            if (counted == false) {
                countcm = countcm + calib;
                counted = true;
            }
        }
        else if ((rp_array == (0,1)) || (rp_array == (1,2)) || (rp_array == (2,3)) || (rp_array == (3,0))) {
            if (counted == false) {
                countcm = countcm - calib;
                counted = true;
            }
        }
        if (oldcount != countcm) {
            FILE * givarna;
            //printf("%d\n", countcm);
            givarna = fopen("/dev/shm/givarna","w+");
            fprintf(givarna, "%ld", countcm);
            fclose(givarna);
        }
        usleep(1);
    }
    return 0;
}
