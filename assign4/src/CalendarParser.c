/*

* Cis2750 F2017

* Assignment 4

* Greg Hetherington 0936504

* file contains a Parser for the iCalendar file format

* Resources:

    -Data Structures (Cis2520) with fangji Wang
    -Cis2750 Lectures with Denis Nikitenko
    -Stackoverflow.com
    -tutoriaalpoint.com

*/

#include "CalendarParser.h"
#include <ctype.h>

int isDateTimeMalformed(char *dateTime) {
    if (dateTime == NULL || strcmp(dateTime, "") == 0) {
        return 0;
    }
    if (dateTime[8] != 'T') {
        return 0;
    }
    for (int i = 0; i < strlen(dateTime); i++) {
        if (i < 8) {
            if (!isdigit(dateTime[i])) {
                return 0;
            }
        } else if (i > 8 && i < 15) {
            if (!isdigit(dateTime[i])) {
                return 0;
            }
        }
    }
    return 1;
}

int isVersionMalformed(char * version) {
    if (version == NULL || strcmp(version, "") == 0) {
        return 0;
    }
    int numberOfDecimals = 0;
    for (int i = 0; i < strlen(version); i++) {
        if (!isdigit(version[i]) && version[i] != '.') {
            return 0;
        } else if (version[i] == '.') {
            numberOfDecimals++;
            if (numberOfDecimals > 1) {
                return 0;
            }
        }
    }
    return 1;
}

char* getFileExtention(char *fileName) {
    char *fileExt = strrchr(fileName, '.');
    if (!fileExt || fileExt == fileName) {
        return "";
    }
    return fileExt + 1;
}

void addEndToString(char *str) {
    int count = 0;
    for (int i = 0; str[i]; i++) {
      if (str[i] == '\r') {
          count++;
          break;
      }
        count++;
    }
    str[count - 1] = '\0';
}

int isStringOnlySpaces(char *str) {
    int spaceCount = 0;
    for (int i = 0; str[i]; i++) {
        if (str[i] == ' ') {
            spaceCount++;
        }
    }
    if (spaceCount == strlen(str)) {
        return 1;
    } else {
        return 0;
    }
}

int getFileLenght(char *fileName) {
    int fileLenght = 0;
    if (fileName == NULL) {
        return 0;
    }
    FILE *f;
    f = fopen(fileName, "r");
    char line[3000];
    if (f == NULL) {
        return 0;
    }
    while (fgets(line, sizeof(line), f) != NULL) {
        for (int i = 0; line[i] != '\0'; i++) {
            if (line[i] == ';') {
                break;
            } else if (line[i] != ' ') {
                addEndToString(line);
                if (isStringOnlySpaces(line) == 0) {
                    fileLenght++;
                }
                break;
            }
        }
    } fclose(f);
    return fileLenght;
}

void propDestroy(void *data) {
    free(data);
}
void alarmDestroy(void *data) {
    Alarm* tmpAlarm;
    tmpAlarm = (Alarm*)data;
    clearList(&tmpAlarm->properties);
    free(tmpAlarm->trigger);
    free(tmpAlarm);
}
void eventDestroy(void *data) {
    Event* tmpEvent;
    tmpEvent = (Event*)data;
    clearList(&tmpEvent->properties);
    clearList(&tmpEvent->alarms);
    free(tmpEvent);
}
char * printAlarm(void *toBePrinted) {
    char* tmpStr;
    Alarm* tmpName;
    int len;

    if (toBePrinted == NULL) {
        return NULL;
    }

    tmpName = (Alarm*)toBePrinted;

    len = strlen(tmpName->action)+strlen(tmpName->trigger)+40;
    tmpStr = (char*)malloc(sizeof(char)*len);

    sprintf(tmpStr, "Action:%s Trigger:%s\n", tmpName->action, tmpName->trigger);
    return tmpStr;
}
char * printProp(void *toBePrinted) {
    char* tmpStr;
    Property* tmpName;
    int len;

    if (toBePrinted == NULL) {
        return NULL;
    }

    tmpName = (Property*)toBePrinted;

    len = strlen(tmpName->propName)+strlen(tmpName->propDescr)+40;
    tmpStr = (char*)malloc(sizeof(char)*len);

    sprintf(tmpStr, "Name:%s Descr:%s\n", tmpName->propName, tmpName->propDescr);

    return tmpStr;
}
char * printEvent(void *toBePrinted) {
    char* tmpStr;
    Event* tmpName;
    int len;

    if (toBePrinted == NULL) {
        return NULL;
    }

    tmpName = (Event*)toBePrinted;

    len = strlen(tmpName->UID)+strlen(tmpName->creationDateTime.date)+strlen(tmpName->creationDateTime.time)+40;
    tmpStr = (char*)malloc(sizeof(char)*len);
    sprintf(tmpStr, "UID:%s Date:%s Time:%s\n", tmpName->UID, tmpName->creationDateTime.date, tmpName->creationDateTime.time);

    return tmpStr;
}
int testCompare(const void * one, const void * two) {
    return strcmp((char*)one, (char*)two);
}

bool compareProp(const void * first, const void * second) {
  Property* tmpProp1;
  Property* tmpProp2;

  if (first == NULL || second == NULL){
      return false;
  }

  tmpProp1 = (Property*)first;
  tmpProp2 = (Property*)second;

  if (strcmp(tmpProp1->propName, tmpProp2->propName) == 0) {
      return true;
  } else {
      return false;
  }
}

Calendar * createSimpleCalendar(char a[1][1000]) {
    Calendar * cal = malloc(sizeof(Calendar));

    cal->version = 2.0;
    strcpy(cal->prodID, a[0]);

    cal->events = initializeList(printEvent, eventDestroy, testCompare);
    cal->properties = initializeList(printProp, propDestroy, testCompare);
    
    return cal;
}

Calendar * createEvent(Calendar * cal, char a[3][1000]) {
  Event * newEvent = malloc(sizeof(Event));
    strcpy(newEvent->UID, a[0]);

    newEvent->properties = initializeList(printProp, propDestroy, testCompare);
    newEvent->alarms = initializeList(printAlarm, alarmDestroy, testCompare);
    
    if (strchr(a[1], 'T') != NULL && strlen(a[1]) > 14) {
    
    char date[9];
    char time[7];
    strncpy(date, a[1], 8);
    date[8] = '\0';
    char* p = strchr(a[1], 'T');
    for(int i = 1; i < 7; i++) {
      time[i-1] = p[i];
      time[i] = '\0';
    }
    if (p[7] == 'Z') {
      newEvent->startDateTime.UTC = true;
    } else {
      newEvent->startDateTime.UTC = false;
    }
    strcpy(newEvent->startDateTime.time, time);
    strcpy(newEvent->startDateTime.date, date);

    } else {
          strcpy(newEvent->startDateTime.time, "");
          strcpy(newEvent->startDateTime.date, "");
    }
    
    if (strchr(a[2], 'T') != NULL && strlen(a[2]) > 14) {
    
    char date[9];
    char time[7];
    strncpy(date, a[2], 8);
    date[8] = '\0';
    char* p = strchr(a[2], 'T');
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

    //Property * p = malloc(sizeof(Property) + sizeof(char)*(6 + strlen(a[3])));
    //strcpy(p->propName, "DTEND");
    //strcpy(p->propDescr, a[3]);
    //insertBack(&newEvent->properties, p);
    
    insertBack(&cal->events, newEvent);
    return cal;
}

Calendar * createAlarm(Calendar * obj, char a[2][1000], int eventNum) {
  if (obj->events.head != NULL) {
        Event* elemE;
        ListIterator iterE = createIterator(obj->events);
        int i = 0;
    while ((elemE = nextElement(&iterE)) != NULL) {
        Event * event = elemE;
	int k = 0;
	if (i == eventNum) {
	  Alarm * newAlarm = malloc(sizeof(Alarm));
          strcpy(newAlarm->action, a[0]);
          newAlarm->properties = initializeList(printProp, propDestroy, testCompare);
	  newAlarm->trigger = malloc(sizeof(char) * (strlen(a[1]) + 1));
          strcpy(newAlarm->trigger, a[1]);
          insertBack(&event->alarms, newAlarm);
	}
	i++;
    }
  }
  return obj;
}

int getNumOfEvents(Calendar * cal) {
    return getLength(cal->events);
}

int getNumOfProps(Calendar * obj, int eventNum) {

    int props = 0;
    if (obj->events.head != NULL) {
        Event* elemE;
        ListIterator iterE = createIterator(obj->events);
        int i = 0;
	while ((elemE = nextElement(&iterE)) != NULL) {
	  Event * event = elemE;
	  int k = 0;
	  if (event->properties.head != NULL) {
	    Property* elem;
	    ListIterator iter = createIterator(event->properties);

	    while ((elem = nextElement(&iter)) != NULL) {
	      Property * prop = elem;
	      k++;
	    }
	    if (i == eventNum) {
	      props = k;
	    }
	  }
	  i++;
	}
    }
    return props;
}

int getNumOfAlarms(Calendar * obj, int eventNum) {

    int alarms = 0;
    if (obj->events.head != NULL) {
        Event* elemE;
        ListIterator iterE = createIterator(obj->events);
        int i = 0;
    while ((elemE = nextElement(&iterE)) != NULL) {
        Event * event = elemE;
	int k = 0;
	if (event->alarms.head != NULL) {
        Alarm* elem;
        ListIterator iter = createIterator(event->alarms);

        while ((elem = nextElement(&iter)) != NULL) {
            Alarm * alarm = elem;
            k++;
        }
	if (i == eventNum) {
	  alarms = k;
	}
	}
	i++;
    }
    }
    return alarms;
}

char * getSummary(Calendar * obj, int eventNum) {

    int props = 0;
    if (obj->events.head != NULL) {
        Event* elemE;
        ListIterator iterE = createIterator(obj->events);
        int i = 0;
    while ((elemE = nextElement(&iterE)) != NULL) {
        Event * event = elemE;
	if (event->properties.head != NULL) {
	  Property* elem;
	  ListIterator iter = createIterator(event->properties);
	  if (i == eventNum) {
	    while ((elem = nextElement(&iter)) != NULL) {
	      Property * prop = elem;
	      if (strcmp(prop->propName, "SUMMARY") == 0) {
		return prop->propDescr;
	      }
	    }
	    return "";
	  }
	}
	i++;
    }
    }
    return "";
}

char * printAlarmsForEvent(Calendar * obj, int eventNum) {

 char* printStr;
 char* tmpStr;
  
 tmpStr = malloc(sizeof(char)*1000);
 printStr = malloc(sizeof(char)*50000);
  
 if (obj->events.head != NULL) {
    Event* elemE;
    ListIterator iterE = createIterator(obj->events);
    int i = 0;
    while ((elemE = nextElement(&iterE)) != NULL) {
        Event * event = elemE; 
	if (i == eventNum) {
            if (event->alarms.head != NULL) {
                Alarm* elemA;
                ListIterator iterA = createIterator(event->alarms);

                sprintf(tmpStr, "      Alarms:\n");
                strcat(printStr, tmpStr);

                while ((elemA = nextElement(&iterA)) != NULL) {
                    Alarm * alarm = elemA;
                    sprintf(tmpStr, "\t\tAction: %s\n\t\tTrigger: %s\n", alarm->action, alarm->trigger);
                    strcat(printStr, tmpStr);
                    //alarm properties

                    if (alarm->properties.head != NULL) {
                        Property* elem;
                        ListIterator iter = createIterator(alarm->properties);

			sprintf(tmpStr, "\t\tProperties:\n");
			strcat(printStr, tmpStr);
			
                        while ((elem = nextElement(&iter)) != NULL) {
                            Property * prop = elem;
                            sprintf(tmpStr, "\t\t- %s:%s\n", prop->propName, prop->propDescr);
                            strcat(printStr, tmpStr);
                        }
                    }
		    sprintf(tmpStr, "\n");
                    strcat(printStr, tmpStr);
                }
            } else {
	      sprintf(tmpStr, "      No Alarms in Event\n");
              strcat(printStr, tmpStr);
	    }
  	}
	i++;
    }
  }

 printStr[0] = ' ';
 printStr[1] = ' ';
 printStr[2] = ' ';
 printStr[3] = ' ';
 printStr[4] = ' ';
 printStr[5] = ' ';
 
 free(tmpStr);

 return printStr;
}

char * printPropsForEvent(Calendar * obj, int eventNum) {

 char* printStr;
 char* tmpStr;
  
 tmpStr = malloc(sizeof(char)*1000);
 printStr = malloc(sizeof(char)*50000);

 if (obj->events.head != NULL) {
        Event* elemE;
        ListIterator iterE = createIterator(obj->events);
	int i = 0;
        while ((elemE = nextElement(&iterE)) != NULL) {
            Event * event = elemE;
	    if (i == eventNum) {
	      if (event->properties.head != NULL) {
                Property* elem;
                ListIterator iter = createIterator(event->properties);
		sprintf(tmpStr, "      Properties:\n");
		strcat(printStr, tmpStr);
                while ((elem = nextElement(&iter)) != NULL) {
                    Property * prop = elem;
                    sprintf(tmpStr, "\t\t- %s:%s\n", prop->propName, prop->propDescr);
                    strcat(printStr, tmpStr);
                }
              } else {
		sprintf(tmpStr, "      No Optional Properties in Event\n");
		strcat(printStr, tmpStr);
	      }
	    }
	    i++;
	}
 }

 printStr[0] = ' ';
 printStr[1] = ' ';
 printStr[2] = ' ';
 printStr[3] = ' ';
 printStr[4] = ' ';
 printStr[5] = ' ';
 
 free(tmpStr);
 return printStr;
}

char * getOrgForEvent(Calendar * obj, int eventNum) {

  char* printStr;
  char* tmpStr;
  
  tmpStr = malloc(sizeof(char)*1000);
  printStr = malloc(sizeof(char)*50000);
  
  if (obj->events.head != NULL) {
        Event* elemE;
        ListIterator iterE = createIterator(obj->events);
	int i = 0;
        while ((elemE = nextElement(&iterE)) != NULL) {
            Event * event = elemE;
	    if (i == eventNum) {
	      if (event->properties.head != NULL) {
                Property* elem;
                ListIterator iter = createIterator(event->properties);
		
                while ((elem = nextElement(&iter)) != NULL) {
                    Property * prop = elem;
                    if (strcmp(prop->propName, "ORGANIZER") == 0) {
		      
		      char *token;

		      token = strtok(prop->propDescr, ":=");
   
		      while( token != NULL ) {
			sprintf(tmpStr, "%s:", token);
			strcat(printStr, tmpStr);
			
			token = strtok(NULL, ":");
		      }
		    }
                }
              } else {
		//no organizer
	        sprintf(tmpStr, "None");
		strcat(printStr, tmpStr);
	      }
	    }
	    i++;
	}
 }
  free(tmpStr);
  printf("%s", printStr);

 printStr[0] = ' ';
 printStr[1] = ' ';
 printStr[2] = ' ';
 printStr[3] = ' ';
 printStr[4] = ' ';
 printStr[5] = ' ';
  
  return printStr;
}

char * getLocationForEvent(Calendar * obj, int eventNum) {

    int props = 0;
    if (obj->events.head != NULL) {
        Event* elemE;
        ListIterator iterE = createIterator(obj->events);
        int i = 0;
    while ((elemE = nextElement(&iterE)) != NULL) {
        Event * event = elemE;
	if (event->properties.head != NULL) {
	  Property* elem;
	  ListIterator iter = createIterator(event->properties);
	  if (i == eventNum) {
	    while ((elem = nextElement(&iter)) != NULL) {
	      Property * prop = elem;
	      if (strcmp(prop->propName, "LOCATION") == 0) {
		return prop->propDescr;
	      }
	    }
	    return "";
	  }
	}
	i++;
    }
    }
    return "";
}

char * getDatetimeForEvent(Calendar * obj, int eventNum) {

    int props = 0;
    if (obj->events.head != NULL) {
        Event* elemE;
        ListIterator iterE = createIterator(obj->events);
        int i = 0;
      while ((elemE = nextElement(&iterE)) != NULL) {
        Event * event = elemE;
        if (i == eventNum) {
	  return event->startDateTime.date;
	}
	i++;
      }
    }
    return "";
}

/** Function to create a Calendar object based on the contents of an iCalendar file.
 *@pre File name cannot be an empty string or NULL.  File name must have the .ics extension.
       File represented by this name must exist and must be readable.
 *@post Either:
        A valid calendar has been created, its address was stored in the variable obj, and OK was returned
		or
		An error occurred, the calendar was not created, all temporary memory was freed, obj was set to NULL, and the
		appropriate error code was returned
 *@return the error code indicating success or the error encountered when parsing the calendar
 *@param fileName - a string containing the name of the iCalendar file
 *@param a double pointer to a Calendar struct that needs to be allocated
**/
ICalErrorCode createCalendar(char* fileName, Calendar** obj) {
    //read file
    if (fileName == NULL || strcmp(getFileExtention(fileName), "ics") != 0) {
        return INV_FILE;
    }
    FILE *iCalFile;
    iCalFile = fopen(fileName, "r");

    char lineParse[3000];
    if (iCalFile == NULL) {
        return INV_FILE;
    }
    int k = 0;
    int fileLenght = getFileLenght(fileName);
    char** fileContentsData = malloc(fileLenght * sizeof(char *));//malloc
    char** fileContentsType = malloc(fileLenght * sizeof(char *));//malloc

    char** line = malloc(fileLenght * sizeof(char *));

    while (fgets(lineParse, sizeof(lineParse), iCalFile) != NULL) {
        if (lineParse[0] == ';') {

      } else if (lineParse[0] == ' ' || lineParse[0] == '\t') {
            fileLenght--;
            addEndToString(lineParse);
            line[k-1] = realloc(line[k-1], (strlen(lineParse) * sizeof(char)) + strlen(line[k-1]));
            char tmp[75];
            sprintf(tmp, "%s", lineParse);
            strcpy(tmp, tmp + 1);
            strcat(line[k-1], tmp);
        } else if (lineParse[0] != ' ') {
            addEndToString(lineParse);
            line[k] = malloc((strlen(lineParse) + 1) * sizeof(char));
            strcpy(line[k], lineParse);
            k++;
        }
        //printf("line: {%s}\n", line[k-1]);
    }

    k = 0;
    while (k < fileLenght) {
        for (int i = 0; line[k][i] != '\0'; i++) {
            if (line[k][i] == ';') {
                break;
            } else if (line[k][i] != ' ') {
                if (isStringOnlySpaces(line[k]) == 0) {
                    char* type = malloc((strlen(line[k]) + 1) * sizeof(char));//malloc
                    char* data = malloc((strlen(line[k]) + 1) * sizeof(char));//malloc
                    int c = 0;
                    for(int i = 0; i <= strlen(line[k]); i++) {
                        if (c != 0 && line[k][i] != '\0') {
                            data[i-c-1] = line[k][i];
                        } else if ((line[k][i] == ';' || line[k][i] == ':') && c == 0) {
                            type[i] = '\0';
                            c = i;
                        } else if (line[k][i] == '\0') {
                            data[i-c-1] = '\0';
                            break;
                        } else {
                            line[k][i] = toupper(line[k][i]);
                            type[i] = line[k][i];
                        }
                    }
                    fileContentsType[k] = malloc((strlen(type) + 1) * sizeof(char));
                    strcpy(fileContentsType[k], type);

                    fileContentsData[k] = malloc((strlen(data) + 1) * sizeof(char));
                    strcpy(fileContentsData[k], data);

                    //printf("{%s}\n", line[k]);
                    //printf("Type: {%s},Data: {%s}\n", fileContentsType[k], fileContentsData[k]);

                    k++;
                    free(type);
                    free(data);
                }
                break;
            }
        }
    }
    fclose(iCalFile);

    if (strcmp(fileContentsType[0], "BEGIN") != 0 || strcmp(fileContentsData[0], "VCALENDAR") != 0) {
        return INV_CAL;
    }

    Calendar* cal = malloc(sizeof(Calendar));

    ICalErrorCode returnCode = OTHER_ERROR;
    int isTrigger = 0;
    char **state = malloc(10 * sizeof(char *));//malloc
    int stateNum = 0;
    state[stateNum] = "NONE";

    for (int i = 0; i < fileLenght; i++) {
        //printf("State:{%s},Type:{%s},Data:{%s}\n", state[stateNum], fileContentsType[i], fileContentsData[i]);
        if (strcmp(fileContentsType[i], "BEGIN") == 0) {
            stateNum++;
            state[stateNum] = malloc((strlen(fileContentsData[i]) + 1) * sizeof(char));
            if (strcmp(fileContentsData[i], "VCALENDAR") == 0) {
                strcpy(state[stateNum], "VCALENDAR");
                cal->version = -1;
                strcpy(cal->prodID, "-1");
                cal->events = initializeList(printEvent, eventDestroy, testCompare);
                cal->properties = initializeList(printProp, propDestroy, testCompare);
            } else if (strcmp(fileContentsData[i], "VEVENT") == 0) {
                strcpy(state[stateNum], "VEVENT");
                Event * newEvent = malloc(sizeof(Event));
                strcpy(newEvent->UID, "-1");
                strcpy(newEvent->creationDateTime.time, "-1");
                strcpy(newEvent->creationDateTime.date, "-1");
                newEvent->properties = initializeList(printProp, propDestroy, testCompare);
                newEvent->alarms = initializeList(printAlarm, alarmDestroy, testCompare);
                insertBack(&cal->events, newEvent);
            } else if (strcmp(fileContentsData[i], "VALARM") == 0) {
                strcpy(state[stateNum], "VALARM");
                Alarm * newAlarm = malloc(sizeof(Alarm));
                strcpy(newAlarm->action, "-1");
                newAlarm->properties = initializeList(printProp, propDestroy, testCompare);
                Event * event = getFromBack(cal->events);
                insertBack(&event->alarms, newAlarm);
                isTrigger = 0;
            } else {
                strcpy(state[stateNum], "OTHER");
            }
        } else if (strcmp(fileContentsType[i], "END") == 0) {
                if (strcmp(fileContentsData[i], "VCALENDAR") == 0 && strcmp(state[stateNum], "VCALENDAR") == 0) {
                    //check for missing proporties
                    if (returnCode == OTHER_ERROR) {
                        returnCode = OK;
                        if (cal->version == -1 || strcmp(cal->prodID, "-1") == 0 || getFromBack(cal->events) == NULL) {
                            returnCode = INV_CAL;
                        }
                    }
                    free(state[stateNum]);
                    stateNum--;
                } else if (strcmp(fileContentsData[i], "VEVENT") == 0 && strcmp(state[stateNum], "VEVENT") ==0) {
                    //checkfor missing properties
                    Event * event = getFromBack(cal->events);
                    if (returnCode == OTHER_ERROR) {
                        if (strcmp(event->UID, "-1") == 0 || strcmp(event->creationDateTime.time, "-1") == 0 || strcmp(event->creationDateTime.date, "-1") == 0) {
                            returnCode = INV_EVENT;
                        }
                    }
                    free(state[stateNum]);
                    stateNum--;
                } else if (strcmp(fileContentsData[i], "VALARM") == 0 && strcmp(state[stateNum], "VALARM") ==0) {
                    //checkfor missing properties
                    Event * event = getFromBack(cal->events);
                    Alarm * alarm = getFromBack(event->alarms);
                    if (returnCode == OTHER_ERROR) {
                        if (strcmp(alarm->action, "-1") == 0 || isTrigger == 0) {
                            returnCode = INV_ALARM;
                        }
                    }
                    free(state[stateNum]);
                    stateNum--;
                } else if (strcmp(state[stateNum], "OTHER") == 0) {
                    returnCode = INV_CAL;
                    free(state[stateNum]);
                    stateNum--;
                } else {
                    returnCode = INV_CAL;
                }
        } else if (strcmp(fileContentsType[i], "VERSION") == 0 && strcmp(state[stateNum], "VCALENDAR") == 0) {//in create vcal state
            //set version
            if(cal->version != -1) {
                returnCode = DUP_VER;
            } else if (isVersionMalformed(fileContentsData[i]) == 0) {
                returnCode = INV_VER;
            } else {
                cal->version = atof(fileContentsData[i]);
            }
        } else if (strcmp(fileContentsType[i], "PRODID") == 0 && strcmp(state[stateNum], "VCALENDAR") == 0) {
            if(strcmp(cal->prodID, "-1") != 0) {
                returnCode = DUP_PRODID;
            } else if (strcmp(fileContentsData[i], "") == 0 || fileContentsData == NULL) {
                returnCode = INV_PRODID;
            } else {
                strcpy(cal->prodID, fileContentsData[i]);
            }
        } else if (strcmp(fileContentsType[i], "UID") == 0 && strcmp(state[stateNum], "VEVENT") == 0) {
            //set UID
            Event * event = getFromBack(cal->events);
            strcpy(event->UID, fileContentsData[i]);
        } else if (strcmp(fileContentsType[i], "DTSTAMP") == 0 && strcmp(state[stateNum], "VEVENT") == 0) {
            //set DTSTAMP
            if (isDateTimeMalformed(fileContentsData[i]) == 0) {
                returnCode = INV_CREATEDT;
            } else {
                char date[9];
                char time[7];
                strncpy(date, fileContentsData[i], 8);
                date[8] = '\0';
                char* p = strchr(fileContentsData[i], 'T');
                for(int i = 1; i < 7; i++) {
                    time[i-1] = p[i];
                    time[i] = '\0';
                }
                Event * event = getFromBack(cal->events);
                if (p[7] == 'Z') {
                    event->creationDateTime.UTC = true;
                } else {
                    event->creationDateTime.UTC = false;
                }
                strcpy(event->creationDateTime.time, time);
                strcpy(event->creationDateTime.date, date);
            }
          } else if (strcmp(fileContentsType[i], "DTSTART") == 0 && strcmp(state[stateNum], "VEVENT") == 0) {
              //set DTSTART
              if (isDateTimeMalformed(fileContentsData[i]) == 0) {
                  returnCode = INV_CREATEDT;
              } else {
                  char date[9];
                  char time[7];
                  strncpy(date, fileContentsData[i], 8);
                  date[8] = '\0';
                  char* p = strchr(fileContentsData[i], 'T');
                  for(int i = 1; i < 7; i++) {
                      time[i-1] = p[i];
                      time[i] = '\0';
                  }
                  Event * event = getFromBack(cal->events);
                  if (p[7] == 'Z') {
                      event->startDateTime.UTC = true;
                  } else {
                      event->startDateTime.UTC = false;
                  }
                  strcpy(event->startDateTime.time, time);
                  strcpy(event->startDateTime.date, date);
              }
        } else if (strcmp(fileContentsType[i], "ACTION") == 0 && strcmp(state[stateNum], "VALARM") == 0) {
            Event * event = getFromBack(cal->events);
            Alarm * alarm = getFromBack(event->alarms);
            strcpy(alarm->action, fileContentsData[i]);
        } else if (strcmp(fileContentsType[i], "TRIGGER") == 0 && strcmp(state[stateNum], "VALARM") == 0) {
            Event * event = getFromBack(cal->events);
            Alarm * alarm = getFromBack(event->alarms);
            alarm->trigger = malloc(sizeof(char) * (strlen(fileContentsData[i]) + 1));
            strcpy(alarm->trigger, fileContentsData[i]);
            isTrigger = 1;
        } else if (strcmp(state[stateNum], "VALARM") == 0) {//parsing alarm properties
            Event * event = getFromBack(cal->events);
            Alarm * alarm = getFromBack(event->alarms);
            Property * prop = malloc(sizeof(Property) + ((1 + strlen(fileContentsData[i])) *sizeof(char)));
          if (returnCode == OTHER_ERROR) {
            if (strcmp(fileContentsType[i], "") == 0 || fileContentsType[i] == NULL || strcmp(fileContentsData[i], "") == 0 || fileContentsData[i] == NULL) {
                returnCode = INV_ALARM;
            }
            if (findElement(alarm->properties, &compareProp, fileContentsType[i]) != NULL) {
                returnCode = INV_ALARM;
            }
            if (strcmp(fileContentsType[i], "IANA-COMP") == 0 || strcmp(fileContentsType[i], "X-COMP") == 0) {
                returnCode = INV_ALARM;
            }
            if (strcmp(fileContentsType[i], "DURATION") == 0 || strcmp(fileContentsType[i], "REPEAT") == 0 || strcmp(fileContentsType[i], "ATTACH") == 0 || strcmp(fileContentsType[i], "DESCRIPTION") == 0) {
            } else {
                returnCode = INV_ALARM;
            }
          }
            strcpy(prop->propName, fileContentsType[i]);
            strcpy(prop->propDescr, fileContentsData[i]);
            insertBack(&alarm->properties, prop);
        } else if (strcmp(state[stateNum], "VEVENT") == 0) {//parsing event properties
            Event * event = getFromBack(cal->events);
            Property * prop = malloc(sizeof(Property) + sizeof(char)*(1 + strlen(fileContentsData[i])));
          if (returnCode == OTHER_ERROR) {
            if (strcmp(fileContentsType[i], "") == 0 || fileContentsType[i] == NULL || strcmp(fileContentsData[i], "") == 0 || fileContentsData[i] == NULL) {
                returnCode = INV_EVENT;
            }
            if (findElement(event->properties, &compareProp, fileContentsType[i]) != NULL) {
                returnCode = INV_EVENT;
            }
            if (strcmp(fileContentsType[i], "IANA-COMP") == 0 || strcmp(fileContentsType[i], "X-COMP") == 0) {
                returnCode = INV_EVENT;
            }
            if (strcmp(fileContentsType[i], "CLASS") == 0 || strcmp(fileContentsType[i], "CREATED") == 0 || strcmp(fileContentsType[i], "DESCRIPTION") == 0 || strcmp(fileContentsType[i], "GEO") == 0 || strcmp(fileContentsType[i], "LAST-MODIFIED") == 0 || strcmp(fileContentsType[i], "LOCATION") == 0 || strcmp(fileContentsType[i], "ORGANIZER") == 0 || strcmp(fileContentsType[i], "PRIORITY") == 0 || strcmp(fileContentsType[i], "SEQ") == 0 || strcmp(fileContentsType[i], "STATUS") == 0 || strcmp(fileContentsType[i], "SUMMARY") == 0 || strcmp(fileContentsType[i], "TRANSP") == 0 || strcmp(fileContentsType[i], "URL") == 0 || strcmp(fileContentsType[i], "RECURID") == 0 || strcmp(fileContentsType[i], "RRULE") == 0 || strcmp(fileContentsType[i], "DTEND") == 0 || strcmp(fileContentsType[i], "DURATION") == 0 || strcmp(fileContentsType[i], "ATTACH") == 0 || strcmp(fileContentsType[i], "ATTENDEE") == 0 || strcmp(fileContentsType[i], "CATEGORIES") == 0 || strcmp(fileContentsType[i], "COMMENT") == 0 || strcmp(fileContentsType[i], "CONTACT") == 0 || strcmp(fileContentsType[i], "EXDATE") == 0 || strcmp(fileContentsType[i], "RSTATUS") == 0 || strcmp(fileContentsType[i], "RELATED") == 0 || strcmp(fileContentsType[i], "RESOURCES") == 0 || strcmp(fileContentsType[i], "RDATE") == 0 || strcmp(fileContentsType[i], "SEQUENCE") == 0) {
            } else {
                returnCode = INV_EVENT;
            }
          }
            strcpy(prop->propName, fileContentsType[i]);
            strcpy(prop->propDescr, fileContentsData[i]);
            insertBack(&event->properties, prop);
        } else if (strcmp(state[stateNum], "VCALENDAR") == 0) {//parsing vcalendar properties
            Property * prop = malloc(sizeof(Property) + sizeof(char)*(1 + strlen(fileContentsData[i])));
          if (returnCode == OTHER_ERROR) {
            if (strcmp(fileContentsType[i], "") == 0 || fileContentsType[i] == NULL || strcmp(fileContentsData[i], "") == 0 || fileContentsData[i] == NULL) {
                returnCode = INV_CAL;
            }
            if (findElement(cal->properties, &compareProp, fileContentsType[i]) != NULL) {
                returnCode = INV_CAL;
            }
            if (strcmp(fileContentsType[i], "IANA-COMP") == 0 || strcmp(fileContentsType[i], "X-COMP") == 0) {
                returnCode = INV_CAL;
            }
            if (strcmp(fileContentsType[i], "CALSCALE") == 0 || strcmp(fileContentsType[i], "METHOD") == 0) {
            } else {
                returnCode = INV_CAL;
            }
          }
            //check if property is not listed on the website
            strcpy(prop->propName, fileContentsType[i]);
            strcpy(prop->propDescr, fileContentsData[i]);
            insertBack(&cal->properties, prop);
        }
    }

    if (returnCode != OK) {
        deleteCalendar(cal);
    } else {
        *obj = cal;
    }

    for (int i = 0; i < fileLenght; i++) {
        free(fileContentsType[i]);
        free(fileContentsData[i]);
    }
    for (int i = 0; i < fileLenght; i++) {
        free(line[i]);
    }
    free(fileContentsType);
    free(fileContentsData);
    free(line);
    free(state);

    if (returnCode == OTHER_ERROR) {
      return INV_CAL;
    }
    return returnCode;
}


/** Function to delete all calendar content and free all the memory.
 *@pre Calendar object exists, is not null, and has not been freed
 *@post Calendar object had been freed
 *@return none
 *@param obj - a pointer to a Calendar struct
**/

void deleteCalendar(Calendar* obj) {
    //clearList(&obj->properties);
    //clearList(&obj->events);
    //free(obj);

    if (obj->events.head != NULL) {
        Event* elemE;
        ListIterator iterE = createIterator(obj->events);

        while ((elemE = nextElement(&iterE)) != NULL) {
            if (elemE->properties.head != NULL) {
                Property* elemEP;
                ListIterator iterEP = createIterator(elemE->properties);

                while ((elemEP = nextElement(&iterEP)) != NULL) {
                    free(elemEP);
                }
            }
            clearList(&elemE->properties);

            if (elemE->alarms.head != NULL) {
                Alarm* elem;
                ListIterator iter = createIterator(elemE->alarms);

                while ((elem = nextElement(&iter)) != NULL) {
                    free(elem->trigger);
                    if (elem->properties.head != NULL) {
                        Property* elemA;
                        ListIterator iterA = createIterator(elem->properties);

                        while ((elemA = nextElement(&iterA)) != NULL) {
                            free(elemA);
                        }
                    }
                    clearList(&elem->properties);
                    free(elem);
                }
            }
            clearList(&elemE->alarms);
            free(elemE);
        }
    }

    if (obj->properties.head != NULL) {
        Property* elemO;
        ListIterator iterO = createIterator(obj->properties);

        while ((elemO = nextElement(&iterO)) != NULL) {
            free(elemO);
        }
    }

    clearList(&obj->properties);
    clearList(&obj->events);
    free(obj);
}



/** Function to create a string representation of a Calendar object.
 *@pre Calendar object exists, is not null, and is valid
 *@post Calendar has not been modified in any way, and a string representing the Calndar contents has been created
 *@return a string contaning a humanly readable representation of a Calendar object
 *@param obj - a pointer to a Calendar struct
**/

char* printCalendar(const Calendar* obj) {
    char* printStr;
    char* tmpStr;

    if (obj == NULL) {
        return "list is null\n";
    }

    tmpStr = malloc(sizeof(char)*1000);
    printStr = malloc(sizeof(char)*50000);

    sprintf(tmpStr, "Calendar: version = %f, prodID = %s\n", obj->version, obj->prodID);
    strcat(printStr, tmpStr);

    sprintf(tmpStr, "Events:\n");
    strcat(printStr, tmpStr);

    if (obj->events.head != NULL) {
        Event* elemE;
        ListIterator iterE = createIterator(obj->events);

        while ((elemE = nextElement(&iterE)) != NULL) {
            Event * event = elemE;

            sprintf(tmpStr, "\n\tEvent:\tUID = %s\n", event->UID);
            strcat(printStr, tmpStr);

            int UTC = 0;
            if (event->creationDateTime.UTC) {
                UTC = 1;
            }
            sprintf(tmpStr, "\tcreationDateTime = %s:%s, UTC=%d\n", event->creationDateTime.date, event->creationDateTime.time, UTC);
            strcat(printStr, tmpStr);
            //alarm

            if (event->alarms.head != NULL) {
                Alarm* elemA;
                ListIterator iterA = createIterator(event->alarms);

                sprintf(tmpStr, "\tAlarms:\n");
                strcat(printStr, tmpStr);

                while ((elemA = nextElement(&iterA)) != NULL) {
                    Alarm * alarm = elemA;
                    sprintf(tmpStr, "\t\tAction: %s\n\t\tTrigger: %s\n", alarm->action, alarm->trigger);
                    strcat(printStr, tmpStr);
                    //alarm properties
                    sprintf(tmpStr, "\t\tProperties:\n");
                    strcat(printStr, tmpStr);

                    if (alarm->properties.head != NULL) {
                        Property* elem;
                        ListIterator iter = createIterator(alarm->properties);

                        while ((elem = nextElement(&iter)) != NULL) {
                            Property * prop = elem;
                            sprintf(tmpStr, "\t\t- %s:%s\n", prop->propName, prop->propDescr);
                            strcat(printStr, tmpStr);
                        }
                        sprintf(tmpStr, "\n");
                        strcat(printStr, tmpStr);
                    }
                }
            }
            //event properties
            sprintf(tmpStr, "\n\tOther Event properties:\n");
            strcat(printStr, tmpStr);

            if (event->properties.head != NULL) {
                Property* elem;
                ListIterator iter = createIterator(event->properties);

                while ((elem = nextElement(&iter)) != NULL) {
                    Property * prop = elem;
                    sprintf(tmpStr, "\t\t- %s:%s\n", prop->propName, prop->propDescr);
                    strcat(printStr, tmpStr);
                }
            }
        }
    }

    //calendar properties
    sprintf(tmpStr, "\n\tOther iCal properties:\n");
    strcat(printStr, tmpStr);

    if (obj->properties.head != NULL) {
        Property* elem;
        ListIterator iter = createIterator(obj->properties);

        while ((elem = nextElement(&iter)) != NULL) {
            Property * prop = elem;
            sprintf(tmpStr, "\t\t- %s:%s\n", prop->propName, prop->propDescr);
            strcat(printStr, tmpStr);
        }
    }

    free(tmpStr);
    return printStr;
}

char* printError(ICalErrorCode err) {
    if (err == OK) {
        return "OK";
    } else if (err == INV_FILE) {
        return "INV_FILE";
    } else if (err == INV_CAL) {
        return "INV_CAL";
    } else if (err == INV_VER) {
        return "INV_VER";
    } else if (err == INV_PRODID) {
        return "INV_PRODID";
    } else if (err == DUP_VER) {
        return "DUP_VER";
    } else if (err == DUP_PRODID) {
        return "DUP_PRODID";
    } else if (err == INV_EVENT) {
        return "INV_EVENT";
    } else if (err == INV_CREATEDT) {
        return "INV_CREATEDT";
    } else if (err == INV_ALARM) {
        return "INV_EVENT";
    }else if (err == OTHER_ERROR) {
        return "OTHER_ERROR";
    }
    return "OTHER_ERROR";
}

/** Function to writing a Calendar object into a file in iCalendar format.
 *@pre Calendar object exists, is not null, and is valid
  *@post Calendar has not been modified in any way, and a file representing the
          Calendar contents in iCalendar format has been created
           *@return the error code indicating success or the error encountered when parsing the calendar
            *@param obj - a pointer to a Calendar struct
             **/
ICalErrorCode writeCalendar(char* fileName, const Calendar* obj) {

    if (fileName == NULL || strcmp(getFileExtention(fileName), "ics") != 0) {
        return INV_FILE;
    }
    FILE *f = fopen(fileName, "w");

    if (obj == NULL) {
        return INV_CAL;
    }

    char* printStr;
    char* tmpStr;
    tmpStr = (char*)malloc(sizeof(char)*3000);
    printStr = (char*)malloc(sizeof(char)*100000);
    *tmpStr = '\0';
    *printStr = '\0';

    sprintf(tmpStr, "BEGIN:VCALENDAR\r\n");
    strcat(printStr, tmpStr);
    sprintf(tmpStr, "VERSION:%f\r\n", obj->version);
    strcat(printStr, tmpStr);
    sprintf(tmpStr, "PRODID:%s\r\n", obj->prodID);
    strcat(printStr, tmpStr);

    if (obj->events.head != NULL) {
        Event* elemE;
        ListIterator iterE = createIterator(obj->events);

        while ((elemE = nextElement(&iterE)) != NULL) {
            Event * event = elemE;

            sprintf(tmpStr, "BEGIN:VEVENT\r\n");
            strcat(printStr, tmpStr);
            sprintf(tmpStr, "UID:%s\r\n", event->UID);
            strcat(printStr, tmpStr);
	    
            sprintf(tmpStr, "DTSTAMP:%sT%s", event->creationDateTime.date, event->creationDateTime.time);
            strcat(printStr, tmpStr);
	    if (event->creationDateTime.UTC) {
                sprintf(tmpStr, "Z\r\n");
            } else {
                sprintf(tmpStr, "\r\n");
            }
            strcat(printStr, tmpStr);
	    
	    sprintf(tmpStr, "DTSTART:%sT%s", event->startDateTime.date, event->startDateTime.time);
            strcat(printStr, tmpStr);

            if (event->startDateTime.UTC) {
                sprintf(tmpStr, "Z\r\n");
            } else {
                sprintf(tmpStr, "\r\n");
            }
            strcat(printStr, tmpStr);
            //alarm

            if (event->alarms.head != NULL) {
                Alarm* elemA;
                ListIterator iterA = createIterator(event->alarms);

                while ((elemA = nextElement(&iterA)) != NULL) {
                    Alarm * alarm = elemA;

                    sprintf(tmpStr, "BEGIN:VALARM\r\n");
                    strcat(printStr, tmpStr);
                    sprintf(tmpStr, "ACTION:%s\r\n", alarm->action);
                    strcat(printStr, tmpStr);
                    sprintf(tmpStr, "TRIGGER:%s\r\n", alarm->trigger);
                    strcat(printStr, tmpStr);

                    //alarm properties

                    if (alarm->properties.head != NULL) {
                        Property* elem;
                        ListIterator iter = createIterator(alarm->properties);

                        while ((elem = nextElement(&iter)) != NULL) {
                            Property * prop = elem;
                            sprintf(tmpStr, "%s:%s\r\n", prop->propName, prop->propDescr);
                            strcat(printStr, tmpStr);
                        }
                    }
                    sprintf(tmpStr, "END:VALARM\r\n");
                    strcat(printStr, tmpStr);
                }
            }
            //event properties
            if (event->properties.head != NULL) {
                Property* elem;
                ListIterator iter = createIterator(event->properties);

                while ((elem = nextElement(&iter)) != NULL) {
                    Property * prop = elem;
                    sprintf(tmpStr, "%s:%s\r\n", prop->propName, prop->propDescr);
                    strcat(printStr, tmpStr);
                }
            }
            sprintf(tmpStr, "END:VEVENT\r\n");
            strcat(printStr, tmpStr);
        }
    }

    //calendar properties
    if (obj->properties.head != NULL) {
        Property* elem;
        ListIterator iter = createIterator(obj->properties);

        while ((elem = nextElement(&iter)) != NULL) {
            Property * prop = elem;
            sprintf(tmpStr, "%s:%s\r\n", prop->propName, prop->propDescr);
            strcat(printStr, tmpStr);
        }
    }
    sprintf(tmpStr, "END:VCALENDAR\r\n");
    strcat(printStr, tmpStr);

    fprintf(f, "%s", printStr);

    fclose(f);
    free(tmpStr);
    free(printStr);

    return OK;
}

/** Function to validating an existing a Calendar object
 *@pre Calendar object exists and is not null
  *@post Calendar has not been modified in any way
   *@return the error code indicating success or the error encountered when validating the calendar
    *@param obj - a pointer to a Calendar struct
     **/
ICalErrorCode validateCalendar(const Calendar* obj) {

  if (obj == NULL) {
      return INV_CAL;
  }

  //check version and prodID
  if (obj->version == 0.0) {
      return INV_VER;
  }
  if (strcmp(obj->prodID, "") == 0 || obj->prodID == NULL) {
      return INV_PRODID;
  }
  //ical properties
  if (obj->properties.head != NULL) {
      Property* elemP;
      ListIterator iterP = createIterator(obj->properties);
      char tempList[10000] = "PRODIDVERSION";

      while ((elemP = nextElement(&iterP)) != NULL) {
          Property * prop = elemP;
          if (strcmp(prop->propName, "CALSCALE") == 0 || strcmp(prop->propName, "METHOD") == 0) {
          } else {
              return INV_CAL;
          }
          if (strstr(tempList, prop->propName) == NULL) {
              strcat(tempList, prop->propName);
          } else {
            return INV_CAL;
          }
      }
  }
  //check all Events with there UID DTSTAMP
  if (obj->events.head != NULL) {
      Event* elem;
      ListIterator iter = createIterator(obj->events);

      while ((elem = nextElement(&iter)) != NULL) {
          Event * event = elem;

          if (strcmp(event->UID, "") == 0 || event->UID == NULL) {
              return INV_EVENT;
          }
          if (strcmp(event->creationDateTime.time, "") == 0 || event->creationDateTime.time == NULL) {
              return INV_CREATEDT;
          }
          if (strcmp(event->creationDateTime.date, "") == 0 || event->creationDateTime.date == NULL) {
              return INV_CREATEDT;
          }
          //check all  alarms with there action and triggers

          if (event->alarms.head != NULL) {
              Alarm* elemA;
              ListIterator iterA = createIterator(event->alarms);

              while ((elemA = nextElement(&iterA)) != NULL) {
                  Alarm * alarm = elemA;

                  if (strcmp(alarm->action, "") == 0 || alarm->action == NULL) {
                      return INV_ALARM;
                  }
                  if (strcmp(alarm->trigger, "") == 0 || alarm->trigger == NULL) {
                      return INV_ALARM;
                  }
                  //alarm properties
                  if (alarm->properties.head != NULL) {
                      Property* elemAP;
                      ListIterator iterAP = createIterator(alarm->properties);
                      char tempList[10000] = "ACTIONTRIGGER";

                      while ((elemAP = nextElement(&iterAP)) != NULL) {
                          Property * prop = elemAP;
                          if (strcmp(prop->propName, "DURATION") == 0 || strcmp(prop->propName, "REPEAT") == 0 || strcmp(prop->propName, "ATTACH") == 0 || strcmp(prop->propName, "DESCRIPTION") == 0) {
                          } else {
                              return INV_ALARM;
                          }
                          if (strstr(tempList, prop->propName) == NULL) {
                              strcat(tempList, prop->propName);
                          } else {
                            return INV_ALARM;
                          }
                      }
                  }
              }
          }
          //event properties
          if (event->properties.head != NULL) {
              Property* elemE;
              ListIterator iterE = createIterator(event->properties);
              char tempList[10000] = "DTSTAMPUID";

              while ((elemE = nextElement(&iterE)) != NULL) {
                  Property * prop = elemE;
                  if (strcmp(prop->propName, "DTSTART") == 0 || strcmp(prop->propName, "CLASS") == 0 || strcmp(prop->propName, "CREATED") == 0 || strcmp(prop->propName, "DESCRIPTION") == 0 || strcmp(prop->propName, "GEO") == 0 || strcmp(prop->propName, "LAST-MODIFIED") == 0 || strcmp(prop->propName, "LOCATION") == 0 || strcmp(prop->propName, "ORGANIZER") == 0 || strcmp(prop->propName, "PRIORITY") == 0 || strcmp(prop->propName, "SEQ") == 0 || strcmp(prop->propName, "STATUS") == 0 || strcmp(prop->propName, "SUMMARY") == 0 || strcmp(prop->propName, "TRANSP") == 0 || strcmp(prop->propName, "URL") == 0 || strcmp(prop->propName, "RECURID") == 0 || strcmp(prop->propName, "RRULE") == 0 || strcmp(prop->propName, "DTEND") == 0 || strcmp(prop->propName, "DURATION") == 0 || strcmp(prop->propName, "ATTACH") == 0 || strcmp(prop->propName, "ATTENDEE") == 0 || strcmp(prop->propName, "CATEGORIES") == 0 || strcmp(prop->propName, "COMMENT") == 0 || strcmp(prop->propName, "CONTACT") == 0 || strcmp(prop->propName, "EXDATE") == 0 || strcmp(prop->propName, "RSTATUS") == 0 || strcmp(prop->propName, "RELATED") == 0 || strcmp(prop->propName, "RESOURCES") == 0 || strcmp(prop->propName, "RDATE") == 0 || strcmp(prop->propName, "SEQUENCE") == 0) {
                  } else {
                      return INV_EVENT;
                  }
                  if (strstr(tempList, prop->propName) == NULL) {
                      strcat(tempList, prop->propName);
                  } else {
                    return INV_EVENT;
                  }
              }
          }
      }
  } else {
    return INV_CAL;
  }
  return OK;
}
