#include "CalendarParser.h"
#include <unistd.h>

void alarmDestroyM(void *data) {
    Alarm* tmpAlarm;
    tmpAlarm = (Alarm*)data;
    clearList(&tmpAlarm->properties);
    free(tmpAlarm->trigger);
    free(tmpAlarm);
}
void eventDestroyM(void *data) {
    Event* tmpEvent;
    tmpEvent = (Event*)data;
    clearList(&tmpEvent->properties);
    clearList(&tmpEvent->alarms);
    free(tmpEvent);
}

int main(void) {
    char input;
    Calendar* Cal = NULL;
    Calendar* newCal = NULL;

    while (input != '5') {
      printf("Enter 1-5:\n1. Read in a iCalendar file\n2. Print Calendar from option 1\n3. Create a new Calendar\n4. Write Calendar to a file\n5. Quit\n");
      scanf(" %c", &input);

      if (input == '1') {

        Cal = malloc(sizeof(Calendar));

        while (1) {
          int c;
          while ((c = getchar()) != '\n' && c != EOF);

          char in;
          printf("Enter f to enter a Filename(f) or q to Quit(q):\n");
          scanf("%s", &in);

          if (in == 'q') {
            break;
          } else {
            int c;
            while ((c = getchar()) != '\n' && c != EOF);

            char input1[255];
            printf("Enter Filename:\n");
            fgets(input1, 255, stdin);
            char *pos;
            if ((pos=strchr(input1, '\n')) != NULL) {
              *pos = '\0';
            }

            ICalErrorCode err = createCalendar(input1, &Cal);
            if (err == INV_FILE) {
              printf("ICalErrorCode: %s\n", printError(err));printf("fileN:{%s}\n", input1);
              break;
            } else {
              printf("ICalErrorCode: %s\n", printError(err));
              break;
              break;
            }
          }
        }
      } else if (input == '2') {
        printf("\n%s\n", printCalendar(Cal));
      } else if (input == '3') {

        newCal = malloc(sizeof(Calendar));

        newCal->version = -1;
        strcpy(newCal->prodID, "-1");
        newCal->events = initializeList(NULL, eventDestroyM, NULL);

        char strInput[255];

        int c;
        while ((c = getchar()) != '\n' && c != EOF);

        char *pos;

        //version
        printf("Enter the version:\n");
        fgets (strInput, 100, stdin);
        if ((pos=strchr(strInput, '\n')) != NULL) {
          *pos = '\0';
        }
        newCal->version = atof(strInput);
        //prodID
        printf("Enter the prodID:\n");
        fgets (strInput, 100, stdin);
        if ((pos=strchr(strInput, '\n')) != NULL) {
          *pos = '\0';
        }
        strcpy(newCal->prodID, strInput);
        //Event UID and creationDateTime
        Event * newEvent = malloc(sizeof(Event));
        strcpy(newEvent->UID, "-1");
        strcpy(newEvent->creationDateTime.time, "-1");
        strcpy(newEvent->creationDateTime.date, "-1");
        newEvent->alarms = initializeList(NULL, alarmDestroyM, NULL);

        strInput[0] = '\0';
        printf("Enter the UID:\n");
        fgets (strInput, 100, stdin);
        if ((pos=strchr(strInput, '\n')) != NULL) {
          *pos = '\0';
        }
        strcpy(newEvent->UID, strInput);

        printf("Enter the creationDateTime: (ie. \"12345678T123456Z\")\n");
        fgets (strInput, 100, stdin);
        if ((pos=strchr(strInput, '\n')) != NULL) {
          *pos = '\0';
        }

        if (strchr(strInput, 'T') != NULL && strlen(strInput) > 14) {
          char date[9];
          char time[7];
          strncpy(date, strInput, 8);
          date[8] = '\0';
          char* p = strchr(strInput, 'T');
          for(int i = 1; i < 7; i++) {
              time[i-1] = p[i];
              time[i] = '\0';
          }
          if (p[7] == 'Z') {
              newEvent->creationDateTime.UTC = true;
          } else {
              newEvent->creationDateTime.UTC = false;
          }
          strcpy(newEvent->creationDateTime.time, time);
          strcpy(newEvent->creationDateTime.date, date);
        } else {
          strcpy(newEvent->creationDateTime.time, "");
          strcpy(newEvent->creationDateTime.date, "");
        }

        //alarm action and trigger
        Alarm * newAlarm = malloc(sizeof(Alarm));
        strcpy(newAlarm->action, "-1");

        printf("Enter the action:\n");
        fgets (strInput, 100, stdin);
        if ((pos=strchr(strInput, '\n')) != NULL) {
          *pos = '\0';
        }
        strcpy(newAlarm->action, strInput);

        printf("Enter the trigger:\n");
        fgets (strInput, 100, stdin);
        if ((pos=strchr(strInput, '\n')) != NULL) {
          *pos = '\0';
        }
        newAlarm->trigger = malloc(sizeof(char) * (strlen(strInput) + 1));
        strcpy(newAlarm->trigger, strInput);

        insertBack(&newEvent->alarms, newAlarm);
        insertBack(&newCal->events, newEvent);

        ICalErrorCode err = validateCalendar(newCal);
        if (err == OK) {
          printf("Create Calendar successful\n");
        } else {
          printf("File create failed ICalErrorCode: %s\n", printError(err));
          deleteCalendar(newCal);
        }

      } else if (input == '4') {

        int c;
        while ((c = getchar()) != '\n' && c != EOF);

        char fileName[255];
        printf("Enter filename to write too:\n");
        fgets(fileName, 255, stdin);
        char *pos;
        if ((pos=strchr(fileName, '\n')) != NULL) {
          *pos = '\0';
        }

        if (access( fileName, F_OK ) != -1 ) {
            // file exists
            char overide;
            printf("Are you sure you what to overide this file? Yes(y) or No(n)\n");
            scanf(" %c", &overide);

            if (overide == 'y') {
              ICalErrorCode writeErr = writeCalendar(fileName, newCal);
              if (writeErr == OK) {
                printf("File write successful\n");
              } else {
                printf("File write failed ICalErrorCode: %s\n", printError(writeErr));
              }
            }

        } else {
            // file doesn't exist
            ICalErrorCode writeErr = writeCalendar(fileName, newCal);
            if (writeErr == OK) {
              printf("File write successful\n");
            } else {
              printf("File write failed ICalErrorCode: %s\n", printError(writeErr));
            }
        }
      } else if (input == '5') {
        break;
      }
    }

    if (Cal != NULL) {
      free(Cal);
    }
    if (newCal != NULL) {
      free(newCal);
    }

    return 0;
}
